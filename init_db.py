#!/usr/bin/env python3
"""
Database initialization script for HydroSpark system
Loads sample data from Excel file
"""

import pandas as pd
from datetime import datetime
from app import create_app
from models import db, User, Customer, Usage

def init_database():
    """Initialize database with schema"""
    print("🔧 Initializing database...")
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("✅ Database schema created")
        
        return app

def create_default_users(app):
    """Create default users for testing"""
    print("👥 Creating default users...")
    
    with app.app_context():
        # Company users
        users_data = [
            {
                'email': 'ops@hydrospark.com',
                'password': 'password123',
                'role': 'operations'
            },
            {
                'email': 'billing@hydrospark.com',
                'password': 'password123',
                'role': 'billing'
            },
            {
                'email': 'support@hydrospark.com',
                'password': 'password123',
                'role': 'support'
            }
        ]
        
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()
        print(f"✅ Created {len(users_data)} company users")

def load_sample_data(app, excel_path):
    """Load sample data from Excel file"""
    print(f"📊 Loading sample data from {excel_path}...")
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_path)
        print(f"   Found {len(df)} usage records")
        
        with app.app_context():
            # Group by customer to create customer records
            customer_groups = df.groupby('Location ID').first()
            
            customers_created = 0
            for location_id, row in customer_groups.iterrows():
                # Check if customer exists
                existing = Customer.query.filter_by(location_id=location_id).first()
                if existing:
                    continue
                
                customer = Customer(
                    name=row['Customer Name'],
                    address=row['Mailing Address'],
                    location_id=location_id,
                    customer_type=row['Customer Type'],
                    cycle_number=row['Cycle Number'],
                    phone=row['Customer Phone Number'],
                    business_name=row['Business Name'] if pd.notna(row['Business Name']) else None,
                    facility_name=row['Facility Name'] if pd.notna(row['Facility Name']) else None
                )
                db.session.add(customer)
                customers_created += 1
            
            db.session.commit()
            print(f"✅ Created {customers_created} customers")
            
            # Create customer user account
            customer = Customer.query.first()
            if customer:
                customer_user = User(
                    email='noah@example.com',
                    role='customer',
                    customer_id=customer.id
                )
                customer_user.set_password('password123')
                db.session.add(customer_user)
                db.session.commit()
                print(f"✅ Created customer user account: noah@example.com")
            
            # Load usage data
            usage_created = 0
            for _, row in df.iterrows():
                customer = Customer.query.filter_by(location_id=row['Location ID']).first()
                if not customer:
                    continue
                
                # Create date from Year, Month, Day columns
                date = datetime(
                    int(row['Year']),
                    int(row['Month']),
                    int(row['Day'])
                ).date()
                
                # Check if usage record exists
                existing = Usage.query.filter_by(
                    customer_id=customer.id,
                    date=date
                ).first()
                
                if existing:
                    continue
                
                usage = Usage(
                    customer_id=customer.id,
                    date=date,
                    usage_ccf=row['Daily Water Usage (CCF)']
                )
                db.session.add(usage)
                usage_created += 1
                
                # Commit in batches
                if usage_created % 500 == 0:
                    db.session.commit()
                    print(f"   Loaded {usage_created} usage records...")
            
            db.session.commit()
            print(f"✅ Created {usage_created} usage records")
            
    except FileNotFoundError:
        print(f"❌ Error: File not found at {excel_path}")
        print("   Skipping sample data load. You can add customers and usage manually.")
    except Exception as e:
        print(f"❌ Error loading sample data: {str(e)}")
        print("   Skipping sample data load.")

def main():
    """Main initialization function"""
    print("=" * 60)
    print("HydroSpark Database Initialization")
    print("=" * 60)
    
    # Initialize database
    app = init_database()
    
    # Create default users
    create_default_users(app)
    
    # Try to load sample data
    excel_path = '/mnt/user-data/uploads/TX_Daily_Water_Usage_101887055.xlsx'
    load_sample_data(app, excel_path)
    
    print()
    print("=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print()
    print("Default Login Credentials:")
    print("-" * 60)
    print("Company Users:")
    print("  Operations: ops@hydrospark.com / password123")
    print("  Billing:    billing@hydrospark.com / password123")
    print("  Support:    support@hydrospark.com / password123")
    print()
    print("Customer:")
    print("  Customer:   noah@example.com / password123")
    print("=" * 60)

if __name__ == '__main__':
    main()
