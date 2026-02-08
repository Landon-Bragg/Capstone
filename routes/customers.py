from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Customer, Usage
from datetime import datetime, timedelta
from sqlalchemy import func

customers_bp = Blueprint('customers', __name__)

def check_access(user, customer_id=None):
    """Check if user has access to customer data"""
    if user.role in ['operations', 'billing', 'support']:
        return True
    if user.role == 'customer' and customer_id and user.customer_id == int(customer_id):
        return True
    return False

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers (company users only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Only company users can see all customers
    if user.role not in ['operations', 'billing', 'support']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    customers = Customer.query.all()
    return jsonify([c.to_dict(include_stats=True) for c in customers]), 200

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get specific customer details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    return jsonify(customer.to_dict(include_stats=True)), 200

@customers_bp.route('/<int:customer_id>/usage', methods=['GET'])
@jwt_required()
def get_customer_usage(customer_id):
    """Get customer usage history"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', type=int)
    
    # Build query
    query = Usage.query.filter_by(customer_id=customer_id).order_by(Usage.date.desc())
    
    if start_date:
        query = query.filter(Usage.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Usage.date <= datetime.fromisoformat(end_date))
    if limit:
        query = query.limit(limit)
    
    usage_records = query.all()
    
    # Calculate summary statistics
    if usage_records:
        total = sum(u.usage_ccf for u in usage_records)
        avg = total / len(usage_records)
        max_usage = max(u.usage_ccf for u in usage_records)
        min_usage = min(u.usage_ccf for u in usage_records)
    else:
        total = avg = max_usage = min_usage = 0
    
    return jsonify({
        'usage': [u.to_dict() for u in usage_records],
        'summary': {
            'total': round(total, 2),
            'average': round(avg, 2),
            'max': round(max_usage, 2),
            'min': round(min_usage, 2),
            'count': len(usage_records)
        }
    }), 200

@customers_bp.route('/<int:customer_id>/usage/monthly', methods=['GET'])
@jwt_required()
def get_monthly_usage(customer_id):
    """Get monthly aggregated usage"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get monthly usage aggregation
    monthly_usage = db.session.query(
        func.strftime('%Y-%m', Usage.date).label('month'),
        func.sum(Usage.usage_ccf).label('total_usage'),
        func.avg(Usage.usage_ccf).label('avg_usage'),
        func.count(Usage.id).label('days')
    ).filter(
        Usage.customer_id == customer_id
    ).group_by(
        func.strftime('%Y-%m', Usage.date)
    ).order_by(
        func.strftime('%Y-%m', Usage.date).desc()
    ).all()
    
    return jsonify([{
        'month': m.month,
        'total_usage': round(m.total_usage, 2),
        'avg_usage': round(m.avg_usage, 2),
        'days': m.days
    } for m in monthly_usage]), 200

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer information"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Only operations and customer themselves can update
    if user.role not in ['operations'] and not (user.role == 'customer' and user.customer_id == customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'address' in data:
        customer.address = data['address']
    if 'phone' in data:
        customer.phone = data['phone']
    if user.role == 'operations':
        if 'customer_type' in data:
            customer.customer_type = data['customer_type']
        if 'cycle_number' in data:
            customer.cycle_number = data['cycle_number']
        if 'business_name' in data:
            customer.business_name = data['business_name']
        if 'facility_name' in data:
            customer.facility_name = data['facility_name']
    
    try:
        db.session.commit()
        return jsonify(customer.to_dict(include_stats=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """Create new customer (operations only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'operations':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'address', 'location_id', 'customer_type', 'cycle_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if location_id already exists
    if Customer.query.filter_by(location_id=data['location_id']).first():
        return jsonify({'error': 'Location ID already exists'}), 409
    
    customer = Customer(
        name=data['name'],
        address=data['address'],
        location_id=data['location_id'],
        customer_type=data['customer_type'],
        cycle_number=data['cycle_number'],
        phone=data.get('phone'),
        business_name=data.get('business_name'),
        facility_name=data.get('facility_name')
    )
    
    try:
        db.session.add(customer)
        db.session.commit()
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
