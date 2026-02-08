from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Customer, Usage, Anomaly
from utils.anomaly_detector import detect_anomalies, analyze_usage_pattern, get_anomaly_summary
from utils.forecasting import forecast_usage, forecast_monthly_bill, get_usage_insights
from datetime import datetime, timedelta

usage_bp = Blueprint('usage', __name__)

def check_access(user, customer_id=None):
    """Check if user has access to usage data"""
    if user.role in ['operations', 'billing', 'support']:
        return True
    if user.role == 'customer' and customer_id and user.customer_id == int(customer_id):
        return True
    return False

@usage_bp.route('/anomalies', methods=['GET'])
@jwt_required()
def get_anomalies():
    """Get usage anomalies"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Build query based on role
    if user.role in ['operations', 'billing', 'support']:
        query = Anomaly.query
    elif user.role == 'customer' and user.customer_id:
        query = Anomaly.query.filter_by(customer_id=user.customer_id)
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Apply filters
    reviewed = request.args.get('reviewed')
    customer_id = request.args.get('customer_id', type=int)
    
    if reviewed is not None:
        reviewed_bool = reviewed.lower() == 'true'
        query = query.filter_by(reviewed=reviewed_bool)
    
    if customer_id and user.role in ['operations', 'billing', 'support']:
        query = query.filter_by(customer_id=customer_id)
    
    anomalies = query.order_by(Anomaly.detected_at.desc()).all()
    
    return jsonify([a.to_dict() for a in anomalies]), 200

@usage_bp.route('/anomalies/detect', methods=['POST'])
@jwt_required()
def detect_new_anomalies():
    """Detect anomalies for all customers or specific customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['operations', 'support']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    customer_id = data.get('customer_id')
    
    if customer_id:
        customers = [Customer.query.get(customer_id)]
        if not customers[0]:
            return jsonify({'error': 'Customer not found'}), 404
    else:
        customers = Customer.query.all()
    
    detected_anomalies = []
    
    for customer in customers:
        # Get usage data
        usage_records = Usage.query.filter_by(customer_id=customer.id).order_by(Usage.date).all()
        
        if len(usage_records) < 30:
            continue
        
        # Prepare data for anomaly detection
        usage_data = [{
            'date': u.date,
            'usage_ccf': u.usage_ccf
        } for u in usage_records]
        
        # Detect anomalies
        anomalies = detect_anomalies(usage_data)
        
        # Save new anomalies
        for anomaly_data in anomalies:
            # Check if already exists
            existing = Anomaly.query.filter_by(
                customer_id=customer.id,
                date=anomaly_data['date']
            ).first()
            
            if not existing:
                anomaly = Anomaly(
                    customer_id=customer.id,
                    date=anomaly_data['date'],
                    usage_ccf=anomaly_data['usage_ccf'],
                    average_usage=anomaly_data['average_usage'],
                    std_deviation=anomaly_data['std_deviation'],
                    sigma_value=anomaly_data['sigma_value']
                )
                db.session.add(anomaly)
                detected_anomalies.append(anomaly)
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Detected {len(detected_anomalies)} new anomalies',
            'anomalies': [a.to_dict() for a in detected_anomalies]
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usage_bp.route('/anomalies/<int:anomaly_id>/review', methods=['POST'])
@jwt_required()
def review_anomaly(anomaly_id):
    """Mark anomaly as reviewed"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['operations', 'support']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    anomaly = Anomaly.query.get(anomaly_id)
    if not anomaly:
        return jsonify({'error': 'Anomaly not found'}), 404
    
    data = request.get_json() or {}
    anomaly.reviewed = True
    anomaly.notes = data.get('notes')
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Anomaly reviewed',
            'anomaly': anomaly.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@usage_bp.route('/forecast/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_forecast(customer_id):
    """Get usage forecast for customer"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Get forecast days from query params
    forecast_days = request.args.get('days', default=30, type=int)
    
    # Get usage data
    usage_records = Usage.query.filter_by(customer_id=customer_id).order_by(Usage.date).all()
    
    usage_data = [{
        'date': u.date,
        'usage_ccf': u.usage_ccf
    } for u in usage_records]
    
    # Generate forecast
    forecast_result = forecast_usage(usage_data, forecast_days=forecast_days)
    
    return jsonify(forecast_result), 200

@usage_bp.route('/forecast/<int:customer_id>/bill', methods=['GET'])
@jwt_required()
def get_forecasted_bill(customer_id):
    """Get forecasted bill for next month"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Get month/year from query params or use next month
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not month or not year:
        # Default to next month
        today = datetime.now()
        next_month = today + timedelta(days=32)
        month = next_month.month
        year = next_month.year
    
    # Get usage data
    usage_records = Usage.query.filter_by(customer_id=customer_id).order_by(Usage.date).all()
    
    usage_data = [{
        'date': u.date,
        'usage_ccf': u.usage_ccf
    } for u in usage_records]
    
    # Generate forecast
    forecast_result = forecast_monthly_bill(usage_data, month, year)
    
    return jsonify(forecast_result), 200

@usage_bp.route('/analytics/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_analytics(customer_id):
    """Get usage analytics and insights"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not check_access(user, customer_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    # Get usage data
    usage_records = Usage.query.filter_by(customer_id=customer_id).order_by(Usage.date).all()
    
    usage_data = [{
        'date': u.date,
        'usage_ccf': u.usage_ccf
    } for u in usage_records]
    
    # Get pattern analysis
    pattern_analysis = analyze_usage_pattern(usage_data)
    
    # Get usage insights
    insights = get_usage_insights(usage_data)
    
    # Get anomaly summary
    anomalies = Anomaly.query.filter_by(customer_id=customer_id).all()
    anomaly_list = [{
        'date': a.date,
        'usage_ccf': a.usage_ccf,
        'average_usage': a.average_usage,
        'std_deviation': a.std_deviation,
        'sigma_value': a.sigma_value,
        'deviation_percent': round(((a.usage_ccf - a.average_usage) / a.average_usage) * 100, 1) if a.average_usage > 0 else 0
    } for a in anomalies]
    
    anomaly_summary = get_anomaly_summary(anomaly_list)
    
    return jsonify({
        'customer': customer.to_dict(),
        'pattern_analysis': pattern_analysis,
        'insights': insights,
        'anomaly_summary': anomaly_summary
    }), 200

@usage_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_usage_data():
    """Upload usage data (operations only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role != 'operations':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data or 'records' not in data:
        return jsonify({'error': 'Invalid data format'}), 400
    
    added = 0
    errors = []
    
    for record in data['records']:
        try:
            # Validate required fields
            if not all(k in record for k in ['customer_id', 'date', 'usage_ccf']):
                errors.append({'record': record, 'error': 'Missing required fields'})
                continue
            
            # Check if customer exists
            customer = Customer.query.get(record['customer_id'])
            if not customer:
                errors.append({'record': record, 'error': 'Customer not found'})
                continue
            
            # Parse date
            date = datetime.fromisoformat(record['date']).date()
            
            # Check if record already exists
            existing = Usage.query.filter_by(
                customer_id=record['customer_id'],
                date=date
            ).first()
            
            if existing:
                # Update existing
                existing.usage_ccf = record['usage_ccf']
            else:
                # Create new
                usage = Usage(
                    customer_id=record['customer_id'],
                    date=date,
                    usage_ccf=record['usage_ccf']
                )
                db.session.add(usage)
            
            added += 1
            
        except Exception as e:
            errors.append({'record': record, 'error': str(e)})
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Processed {added} usage records',
            'added': added,
            'errors': errors
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
