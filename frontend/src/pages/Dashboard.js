import React, { useState, useEffect } from 'react';
import { billsAPI, customersAPI, usageAPI } from '../services/api';

function Dashboard({ user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [billSummary, customers, anomalies] = await Promise.all([
        billsAPI.getSummary(),
        customersAPI.getAll(),
        usageAPI.getAnomalies({ reviewed: false }),
      ]);

      setStats({
        bills: billSummary.data,
        totalCustomers: customers.data.length,
        pendingAnomalies: anomalies.data.length,
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <h1>Company Dashboard</h1>
      <p>Welcome, {user.email}</p>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Customers</div>
          <div className="stat-value">{stats.totalCustomers}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Bills</div>
          <div className="stat-value">{stats.bills.counts.pending}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Outstanding Revenue</div>
          <div className="stat-value">${stats.bills.revenue.outstanding.toFixed(2)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Anomalies</div>
          <div className="stat-value">{stats.pendingAnomalies}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">Revenue Overview</div>
        <div className="grid-2">
          <div>
            <p><strong>Total Collected:</strong> ${stats.bills.revenue.total_collected.toFixed(2)}</p>
            <p><strong>Pending:</strong> ${stats.bills.revenue.pending.toFixed(2)}</p>
          </div>
          <div>
            <p><strong>Total Bills:</strong> {stats.bills.counts.total}</p>
            <p><strong>Paid Bills:</strong> {stats.bills.counts.paid}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
