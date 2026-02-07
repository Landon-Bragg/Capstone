import os
from datetime import timedelta

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///hydrospark.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'hydrospark-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # App
    SECRET_KEY = os.getenv('SECRET_KEY', 'hydrospark-flask-secret-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Pricing Configuration
    PRICING = {
        'tiers': [
            {'min': 0, 'max': 10, 'rate': 2.50},
            {'min': 10, 'max': 20, 'rate': 3.00},
            {'min': 20, 'max': float('inf'), 'rate': 3.50}
        ],
        'seasonal_multipliers': {
            'summer': 1.2,  # June, July, August
            'winter': 0.9,  # December, January, February
            'spring_fall': 1.0  # March, April, May, September, October, November
        },
        'fees': {
            'base_service': 15.00,
            'infrastructure': 5.00
        }
    }
    
    # Anomaly Detection
    ANOMALY_THRESHOLD_SIGMA = 2.0  # Standard deviations
    
    # Email Configuration (for future implementation)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
