from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Customer, Bill, Usage
from utils.billing_calculator import calculate_total_bill, generate_bill_summary
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import func

billing_bp = Blueprint('billing', __name__)

@billing_bp.route('', methods=['GET'])
@jwt_required()
def get_bills():
    """Get bills (filtered by role)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Build query based on role
    if user.role in ['operations', 'billing', 'support']:
        # Company users see all bills
        query = Bill.query
    elif user.role == 'customer' and user.customer_id:
        # Customers see only their bills
        query = Bill.query.filter_by(customer_id=user.customer_id)
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Apply filters
    status = request.args.get('status')
    customer_id = request.args.get('customer_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if status:
        query = query.filter_by(status=status)
    if customer_id and user.role in ['operations', 'billing', 'support']:
        query = query.filter_by(customer_id=customer_id)
    if start_date:
        query = query.filter(Bill.billing_period_start >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Bill.billing_period_end <= datetime.fromisoformat(end_date))
    
    bills = query.order_by(Bill.generated_at.desc()).all()
    
    return jsonify([b.to_dict() for b in bills]), 200

@billing_bp.route('/<int:bill_id>', methods=['GET'])
@jwt_required()
def get_bill(bill_id):
    """Get specific bill details"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    # Check access
    if user.role == 'customer' and user.customer_id != bill.customer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(bill.to_dict()), 200

@billing_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_bills():
    """Generate bills for all customers or specific period (billing role only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['billing', 'operations']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() or {}
    
    # Get period from request or use last month
    if 'year' in data and 'month' in data:
        year = data['year']
        month = data['month']
    else:
        # Default to previous month
        today = datetime.now()
        first_of_month = today.replace(day=1)
        last_month = first_of_month - timedelta(days=1)
        year = last_month.year
        month = last_month.month
    
    # Calculate period dates
    period_start = datetime(year, month, 1).date()
    period_end = (datetime(year, month, 1) + relativedelta(months=1) - timedelta(days=1)).date()
    
    # Get customer_id if specified
    customer_id = data.get('customer_id')
    
    if customer_id:
        customers = [Customer.query.get(customer_id)]
        if not customers[0]:
            return jsonify({'error': 'Customer not found'}), 404
    else:
        customers = Customer.query.all()
    
    generated_bills = []
    errors = []
    
    for customer in customers:
        try:
            # Check if bill already exists for this period
            existing_bill = Bill.query.filter_by(
                customer_id=customer.id,
                billing_period_start=period_start,
                billing_period_end=period_end
            ).first()
            
            if existing_bill:
                errors.append({
                    'customer_id': customer.id,
                    'error': 'Bill already exists for this period'
                })
                continue
            
            # Get usage for the period
            usage_records = Usage.query.filter(
                Usage.customer_id == customer.id,
                Usage.date >= period_start,
                Usage.date <= period_end
            ).all()
            
            if not usage_records:
                errors.append({
                    'customer_id': customer.id,
                    'error': 'No usage data for this period'
                })
                continue
            
            total_usage = sum(u.usage_ccf for u in usage_records)
            
            # Calculate bill
            bill_calc = calculate_total_bill(total_usage, month)
            
            # Create bill record
            bill = Bill(
                customer_id=customer.id,
                billing_period_start=period_start,
                billing_period_end=period_end,
                total_usage=bill_calc['total_usage'],
                base_charge=bill_calc['breakdown']['usage_charge'],
                usage_charge=bill_calc['usage_charge'],
                fees=bill_calc['total_fees'],
                total_amount=bill_calc['total_amount'],
                status='pending'
            )
            
            db.session.add(bill)
            generated_bills.append(bill)
            
        except Exception as e:
            errors.append({
                'customer_id': customer.id,
                'error': str(e)
            })
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'Generated {len(generated_bills)} bills',
            'bills': [b.to_dict() for b in generated_bills],
            'errors': errors
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/<int:bill_id>/send', methods=['POST'])
@jwt_required()
def send_bill(bill_id):
    """Mark bill as sent (in production, would send email)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['billing', 'operations']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    bill.status = 'sent'
    bill.sent_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # In production, would send email here
        # send_email(bill.customer.email, bill_summary, bill.to_dict())
        
        return jsonify({
            'message': 'Bill sent successfully',
            'bill': bill.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/<int:bill_id>/pay', methods=['POST'])
@jwt_required()
def mark_paid(bill_id):
    """Mark bill as paid"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    bill = Bill.query.get(bill_id)
    if not bill:
        return jsonify({'error': 'Bill not found'}), 404
    
    # Check access
    if user.role not in ['billing', 'operations'] and user.customer_id != bill.customer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bill.status = 'paid'
    bill.paid_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Bill marked as paid',
            'bill': bill.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@billing_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_billing_summary():
    """Get billing summary statistics (company users only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role not in ['billing', 'operations', 'support']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get summary statistics
    total_bills = Bill.query.count()
    pending_bills = Bill.query.filter_by(status='pending').count()
    sent_bills = Bill.query.filter_by(status='sent').count()
    paid_bills = Bill.query.filter_by(status='paid').count()
    
    total_revenue = db.session.query(func.sum(Bill.total_amount)).filter_by(status='paid').scalar() or 0
    pending_revenue = db.session.query(func.sum(Bill.total_amount)).filter_by(status='pending').scalar() or 0
    outstanding_revenue = db.session.query(func.sum(Bill.total_amount)).filter_by(status='sent').scalar() or 0
    
    return jsonify({
        'counts': {
            'total': total_bills,
            'pending': pending_bills,
            'sent': sent_bills,
            'paid': paid_bills
        },
        'revenue': {
            'total_collected': round(total_revenue, 2),
            'pending': round(pending_revenue, 2),
            'outstanding': round(outstanding_revenue, 2)
        }
    }), 200
