import React, { useState } from 'react';
import { authAPI } from '../services/api';

function Login({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authAPI.login(email, password);
      onLogin(response.data.user, response.data.access_token);
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (email, password) => {
    setEmail(email);
    setPassword(password);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo">
          Hydro<span>Spark</span>
        </div>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-control"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '4px' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
            Quick Login (Demo):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
            <button
              type="button"
              onClick={() => quickLogin('noah@example.com', 'password123')}
              style={{ padding: '0.5rem', textAlign: 'left', border: '1px solid #ddd', borderRadius: '4px', background: 'white', cursor: 'pointer' }}
            >
              👤 Customer: noah@example.com
            </button>
            <button
              type="button"
              onClick={() => quickLogin('ops@hydrospark.com', 'password123')}
              style={{ padding: '0.5rem', textAlign: 'left', border: '1px solid #ddd', borderRadius: '4px', background: 'white', cursor: 'pointer' }}
            >
              🏢 Operations: ops@hydrospark.com
            </button>
            <button
              type="button"
              onClick={() => quickLogin('billing@hydrospark.com', 'password123')}
              style={{ padding: '0.5rem', textAlign: 'left', border: '1px solid #ddd', borderRadius: '4px', background: 'white', cursor: 'pointer' }}
            >
              💰 Billing: billing@hydrospark.com
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
