import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header({ user, onLogout }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          Hydro<span style={{ color: '#1EA7D6' }}>Spark</span>
        </div>
        <nav className="nav">
          <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
            Dashboard
          </Link>
          <Link to="/bills" className={`nav-link ${isActive('/bills') ? 'active' : ''}`}>
            Bills
          </Link>
          {user.role !== 'customer' && (
            <>
              <Link to="/customers" className={`nav-link ${isActive('/customers') ? 'active' : ''}`}>
                Customers
              </Link>
              <Link to="/anomalies" className={`nav-link ${isActive('/anomalies') ? 'active' : ''}`}>
                Anomalies
              </Link>
            </>
          )}
          <Link to="/analytics" className={`nav-link ${isActive('/analytics') ? 'active' : ''}`}>
            Analytics
          </Link>
          <div style={{ marginLeft: '1rem', borderLeft: '1px solid rgba(255,255,255,0.3)', paddingLeft: '1rem' }}>
            <span style={{ marginRight: '1rem', opacity: 0.8 }}>{user.email}</span>
            <button onClick={onLogout} className="btn btn-secondary" style={{ padding: '0.5rem 1rem' }}>
              Logout
            </button>
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Header;
