# HydroSpark Water Usage & Billing System

A comprehensive water utility management system for HydroSpark that handles metering data, billing calculations, anomaly detection, and customer management.


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
Backend runs on `http://localhost:5001`

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


