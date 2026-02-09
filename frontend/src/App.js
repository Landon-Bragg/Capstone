import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';

// Components
import Header from './components/Header';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CustomerDashboard from './pages/CustomerDashboard';
import Bills from './pages/Bills';
import Customers from './pages/Customers';
import Anomalies from './pages/Anomalies';
import Analytics from './pages/Analytics';

import { authAPI } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await authAPI.getCurrentUser();
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  };

  const handleLogin = (userData, token) => {
    console.log('handleLogin called with:', userData, token);
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
    console.log('Token saved:', localStorage.getItem('token'));
  };
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="app">
        {user && <Header user={user} onLogout={handleLogout} />}
        <div className="main-content">
          <Routes>
            <Route
              path="/login"
              element={!user ? <Login onLogin={handleLogin} /> : <Navigate to="/" />}
            />
            <Route
              path="/"
              element={
                user ? (
                  user.role === 'customer' ? (
                    <CustomerDashboard user={user} />
                  ) : (
                    <Dashboard user={user} />
                  )
                ) : (
                  <Navigate to="/login" />
                )
              }
            />
            <Route
              path="/bills"
              element={user ? <Bills user={user} /> : <Navigate to="/login" />}
            />
            <Route
              path="/customers"
              element={
                user && user.role !== 'customer' ? (
                  <Customers user={user} />
                ) : (
                  <Navigate to="/" />
                )
              }
            />
            <Route
              path="/anomalies"
              element={
                user && user.role !== 'customer' ? (
                  <Anomalies user={user} />
                ) : (
                  <Navigate to="/" />
                )
              }
            />
            <Route
              path="/analytics"
              element={user ? <Analytics user={user} /> : <Navigate to="/login" />}
            />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
