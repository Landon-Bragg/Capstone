# HydroSpark Water Usage & Billing System

A comprehensive water utility management system for HydroSpark that handles metering data, billing calculations, anomaly detection, and customer management.

## Features

### Company-Facing Application
- **Generate & Send Customer Bills** - Automated billing with tiered and seasonal pricing
- **Identify Water Usage Anomalies** - Statistical anomaly detection (2σ threshold)
- **Access Control** - Role-based access for Operations, Billing, and Support teams
- **Customer Management** - View and manage customer accounts
- **Usage Analytics** - Historical usage patterns and trends

### Customer-Facing Application
- **Anticipated Bill Amounts** - Forecasted billing based on historical usage
- **Historical Water Usage** - Interactive charts and data visualization
- **Bill History** - View past bills and payment status
- **Profile Management** - Update contact information

## Tech Stack

- **Backend**: Python 3.8+, Flask, SQLAlchemy
- **Frontend**: React 18, Recharts, Axios
- **Database**: SQLite (production-ready for MySQL/MariaDB)
- **Authentication**: JWT with bcrypt password hashing

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd hydrospark-system
```

2. **Backend Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database and load sample data
python init_db.py
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

1. **Start Backend** (from project root)
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```
Backend runs on `http://localhost:5000`

2. **Start Frontend** (in a new terminal)
```bash
cd frontend
npm start
```
Frontend runs on `http://localhost:3000`

### Default Login Credentials

**Company Users:**
- Operations Manager: `ops@hydrospark.com` / `password123`
- Billing Admin: `billing@hydrospark.com` / `password123`
- Support Staff: `support@hydrospark.com` / `password123`

**Customer:**
- Noah Hernandez: `noah@example.com` / `password123`

## Project Structure

```
hydrospark-system/
├── app.py                 # Flask application entry point
├── models.py              # Database models
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── routes/
│   ├── auth.py           # Authentication endpoints
│   ├── billing.py        # Billing operations
│   ├── customers.py      # Customer management
│   └── usage.py          # Usage data and analytics
├── utils/
│   ├── anomaly_detector.py  # Anomaly detection logic
│   ├── billing_calculator.py # Billing calculations
│   └── forecasting.py    # Usage forecasting
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/   # React components
    │   ├── pages/        # Page components
    │   ├── services/     # API services
    │   └── App.js        # Main app component
    └── package.json
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Billing
- `GET /api/bills` - Get bills (filtered by role)
- `POST /api/bills/generate` - Generate monthly bills
- `GET /api/bills/:id` - Get specific bill
- `POST /api/bills/:id/send` - Send bill via email

### Customers
- `GET /api/customers` - List all customers (company only)
- `GET /api/customers/:id` - Get customer details
- `GET /api/customers/:id/usage` - Get usage history

### Usage & Anomalies
- `GET /api/usage/anomalies` - Detect usage anomalies
- `GET /api/usage/forecast/:customerId` - Get usage forecast
- `GET /api/usage/analytics/:customerId` - Get usage analytics

## Pricing Structure

### Tiered Pricing (Base Rates)
- Tier 1: 0-10 CCF @ $2.50/CCF
- Tier 2: 10-20 CCF @ $3.00/CCF
- Tier 3: 20+ CCF @ $3.50/CCF

### Seasonal Multipliers
- Summer (June-August): 1.2x
- Winter (December-February): 0.9x
- Spring/Fall: 1.0x

### Additional Fees
- Base Service Fee: $15.00/month
- Infrastructure Fee: $5.00/month

## Anomaly Detection

The system uses statistical analysis to detect unusual water usage:
- Calculates mean and standard deviation for each customer
- Flags usage > 2 standard deviations above customer's average
- Generates alerts for operations team review

## Database Schema

### Users Table
- id, email, password_hash, role, customer_id, created_at

### Customers Table
- id, name, address, location_id, customer_type, cycle_number, phone, business_name, facility_name, created_at

### Usage Table
- id, customer_id, date, usage_ccf, created_at

### Bills Table
- id, customer_id, billing_period_start, billing_period_end, total_usage, base_charge, usage_charge, fees, total_amount, status, generated_at, sent_at

### Anomalies Table
- id, customer_id, date, usage_ccf, average_usage, std_deviation, detected_at, reviewed

## Deployment Notes

### Switching to MySQL/MariaDB

1. Update `config.py`:
```python
SQLALCHEMY_DATABASE_URI = 'mysql://user:password@localhost/hydrospark'
```

2. Install MySQL driver:
```bash
pip install pymysql
```

3. Re-run database initialization

## Development

### Adding New Features
1. Create database models in `models.py`
2. Add API routes in appropriate `routes/` file
3. Create frontend components in `frontend/src/components/`
4. Update API services in `frontend/src/services/`

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

## Support

For issues or questions, contact the development team or create an issue in the repository.

## License

Proprietary - HydroSpark Inc.
