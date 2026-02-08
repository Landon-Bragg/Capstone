import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { customersAPI, billsAPI, usageAPI } from '../services/api';

function CustomerDashboard({ user }) {
  const [customer, setCustomer] = useState(null);
  const [usage, setUsage] = useState([]);
  const [forecastedBill, setForecastedBill] = useState(null);
  const [recentBills, setRecentBills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user.customer_id) {
      loadData();
    }
  }, [user]);

  const loadData = async () => {
    try {
      const [customerRes, usageRes, billsRes, forecastRes] = await Promise.all([
        customersAPI.getById(user.customer_id),
        customersAPI.getMonthlyUsage(user.customer_id),
        billsAPI.getAll(),
        usageAPI.getForecastedBill(user.customer_id),
      ]);

      setCustomer(customerRes.data);
      setUsage(usageRes.data);
      setRecentBills(billsRes.data.slice(0, 5));
      setForecastedBill(forecastRes.data);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (!customer) {
    return <div className="alert alert-error">Customer data not found</div>;
  }

  return (
    <div>
      <h1>Welcome, {customer.name}</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Average Daily Usage</div>
          <div className="stat-value">{customer.stats?.avg_daily_usage?.toFixed(2) || 0} CCF</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Next Estimated Bill</div>
          <div className="stat-value">
            ${forecastedBill?.total_amount?.toFixed(2) || 'N/A'}
          </div>
          {forecastedBill && (
            <div className="stat-change">Based on current usage patterns</div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">Monthly Water Usage</div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={usage}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis label={{ value: 'Usage (CCF)', angle: -90, position: 'insideLeft' }} />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total_usage" stroke="#1EA7D6" name="Usage (CCF)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <div className="card-header">Recent Bills</div>
        {recentBills.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Period</th>
                <th>Usage</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {recentBills.map((bill) => (
                <tr key={bill.id}>
                  <td>{bill.billing_period_start} to {bill.billing_period_end}</td>
                  <td>{bill.total_usage.toFixed(2)} CCF</td>
                  <td>${bill.total_amount.toFixed(2)}</td>
                  <td>
                    <span className={`badge badge-${bill.status === 'paid' ? 'success' : bill.status === 'sent' ? 'warning' : 'info'}`}>
                      {bill.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No bills available yet.</p>
        )}
      </div>
    </div>
  );
}

export default CustomerDashboard;
