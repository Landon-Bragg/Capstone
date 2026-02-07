from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # customer, operations, billing, support
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'customer_id': self.customer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    location_id = db.Column(db.Integer, unique=True, nullable=False)
    customer_type = db.Column(db.String(50), nullable=False)  # Residential, Commercial
    cycle_number = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    business_name = db.Column(db.String(200), nullable=True)
    facility_name = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    usage_records = db.relationship('Usage', backref='customer', lazy=True, cascade='all, delete-orphan')
    bills = db.relationship('Bill', backref='customer', lazy=True, cascade='all, delete-orphan')
    anomalies = db.relationship('Anomaly', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_stats=False):
        data = {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'location_id': self.location_id,
            'customer_type': self.customer_type,
            'cycle_number': self.cycle_number,
            'phone': self.phone,
            'business_name': self.business_name,
            'facility_name': self.facility_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_stats:
            # Add usage statistics
            total_usage = db.session.query(db.func.sum(Usage.usage_ccf)).filter(
                Usage.customer_id == self.id
            ).scalar() or 0
            
            avg_daily_usage = db.session.query(db.func.avg(Usage.usage_ccf)).filter(
                Usage.customer_id == self.id
            ).scalar() or 0
            
            data['stats'] = {
                'total_usage': float(total_usage),
                'avg_daily_usage': float(avg_daily_usage),
                'total_bills': len(self.bills),
                'anomaly_count': len([a for a in self.anomalies if not a.reviewed])
            }
        
        return data


class Usage(db.Model):
    __tablename__ = 'usage'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    usage_ccf = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('customer_id', 'date', name='unique_customer_date'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'date': self.date.isoformat() if self.date else None,
            'usage_ccf': self.usage_ccf,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Bill(db.Model):
    __tablename__ = 'bills'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    billing_period_start = db.Column(db.Date, nullable=False)
    billing_period_end = db.Column(db.Date, nullable=False)
    total_usage = db.Column(db.Float, nullable=False)
    base_charge = db.Column(db.Float, nullable=False)
    usage_charge = db.Column(db.Float, nullable=False)
    fees = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, sent, paid
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'billing_period_start': self.billing_period_start.isoformat() if self.billing_period_start else None,
            'billing_period_end': self.billing_period_end.isoformat() if self.billing_period_end else None,
            'total_usage': self.total_usage,
            'base_charge': self.base_charge,
            'usage_charge': self.usage_charge,
            'fees': self.fees,
            'total_amount': self.total_amount,
            'status': self.status,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }


class Anomaly(db.Model):
    __tablename__ = 'anomalies'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    usage_ccf = db.Column(db.Float, nullable=False)
    average_usage = db.Column(db.Float, nullable=False)
    std_deviation = db.Column(db.Float, nullable=False)
    sigma_value = db.Column(db.Float, nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'date': self.date.isoformat() if self.date else None,
            'usage_ccf': self.usage_ccf,
            'average_usage': self.average_usage,
            'std_deviation': self.std_deviation,
            'sigma_value': self.sigma_value,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'reviewed': self.reviewed,
            'notes': self.notes
        }
