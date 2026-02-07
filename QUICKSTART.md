# 🚀 HydroSpark Quick Start Guide

This guide will get you up and running in under 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 16+ installed
- Terminal/Command Prompt

## Setup Steps

### 1. Navigate to Project
```bash
cd hydrospark-system
```

### 2. Backend Setup (Terminal 1)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python init_db.py

# Start backend server
python app.py
```

Backend will run on **http://localhost:5000**

### 3. Frontend Setup (Terminal 2)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will open automatically at **http://localhost:3000**

## Login Credentials

### Customer Account
- Email: `noah@example.com`
- Password: `password123`
- Can view: Personal usage, bills, forecasts

### Company Accounts

**Operations Manager**
- Email: `ops@hydrospark.com`
- Password: `password123`
- Can: Manage customers, generate bills, detect anomalies

**Billing Administrator**
- Email: `billing@hydrospark.com`
- Password: `password123`
- Can: Generate bills, send bills, view revenue

**Support Staff**
- Email: `support@hydrospark.com`
- Password: `password123`
- Can: View customer data, review anomalies

## Testing the Features

1. **Login** as a customer to see:
   - Personal dashboard with usage charts
   - Monthly usage history
   - Forecasted next bill amount
   - Recent bills

2. **Login** as Operations to:
   - View all customers
   - Generate monthly bills
   - Detect water usage anomalies
   - View company dashboard

3. **Test Billing Flow**:
   - Login as Billing user
   - Click "Bills" → "Generate Bills"
   - View generated bills
   - Click "Send" to mark bills as sent
   - Customer can then see and pay bills

4. **Test Anomaly Detection**:
   - Login as Operations/Support
   - Go to "Anomalies"
   - Click "Detect New Anomalies"
   - Review flagged unusual usage patterns

## Key Features Implemented

✅ **Company-Facing**
- Generate customer bills with tiered & seasonal pricing
- Detect anomalies using 2σ statistical analysis
- Role-based access control (Operations, Billing, Support)
- Customer management
- Revenue tracking & analytics

✅ **Customer-Facing**
- View anticipated bill amounts (forecasted)
- Historical water usage visualization
- Bill history with payment status
- Usage pattern insights

✅ **Technical**
- JWT authentication
- Tiered pricing (0-10 CCF @ $2.50, 10-20 @ $3.00, 20+ @ $3.50)
- Seasonal multipliers (Summer 1.2x, Winter 0.9x)
- Statistical anomaly detection (2 standard deviations)
- Usage forecasting
- RESTful API

## Troubleshooting

**Port already in use?**
- Backend: Change port in `app.py` (default: 5000)
- Frontend: Change in `package.json` or use PORT=3001 npm start

**Database errors?**
- Run `python init_db.py` again to reset database

**API connection errors?**
- Ensure backend is running on port 5000
- Check CORS settings in `config.py`

## Next Steps

- Review `README.md` for detailed documentation
- Check API endpoints in `app.py`
- Customize pricing in `config.py`
- Add more customers via Operations panel
- Explore the code structure

## Support

For issues or questions, check:
- Main `README.md` for full documentation
- Code comments for implementation details
- API documentation at http://localhost:5000/

---

**Happy testing! 💧**
