import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { usageAPI, customersAPI } from '../services/api';

function Analytics({ user }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const customerId = user.role === 'customer' ? user.customer_id : null;

  useEffect(() => {
    if (customerId) {
      loadAnalytics(customerId);
    }
  }, [customerId]);

  const loadAnalytics = async (id) => {
    try {
      const response = await usageAPI.getAnalytics(id);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  if (!customerId) {
    return (
      <div>
        <h1>Analytics</h1>
        <div className="alert alert-info">
          Please select a customer from the Customers page to view analytics.
        </div>
      </div>
    );
  }

  if (!analytics) {
    return <div className="alert alert-error">No analytics data available</div>;
  }

  const dayOfWeekData = analytics.insights?.day_of_week_patterns 
    ? Object.entries(analytics.insights.day_of_week_patterns).map(([day, usage]) => ({
        day,
        usage: Number(usage)
      }))
    : [];

  return (
    <div>
      <h1>Usage Analytics</h1>
      <p>Analysis for {analytics.customer?.name}</p>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Average Daily Usage</div>
          <div className="stat-value">{analytics.insights?.avg_daily_usage?.toFixed(2) || 0} CCF</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Usage Consistency</div>
          <div className="stat-value">{analytics.insights?.usage_consistency || 'N/A'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Highest Usage Day</div>
          <div className="stat-value">{analytics.insights?.highest_usage_day || 'N/A'}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Anomalies Detected</div>
          <div className="stat-value">{analytics.anomaly_summary?.total_anomalies || 0}</div>
        </div>
      </div>

      {dayOfWeekData.length > 0 && (
        <div className="card">
          <div className="card-header">Usage by Day of Week</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={dayOfWeekData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis label={{ value: 'Avg Usage (CCF)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="usage" fill="#1EA7D6" name="Average Usage" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {analytics.insights?.recommendations && (
        <div className="card">
          <div className="card-header">Recommendations</div>
          <ul>
            {analytics.insights.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {analytics.pattern_analysis && (
        <div className="card">
          <div className="card-header">Pattern Analysis</div>
          <div className="grid-2">
            <div>
              <p><strong>Mean:</strong> {analytics.pattern_analysis.mean} CCF</p>
              <p><strong>Median:</strong> {analytics.pattern_analysis.median} CCF</p>
              <p><strong>Std Deviation:</strong> {analytics.pattern_analysis.std_dev} CCF</p>
            </div>
            <div>
              <p><strong>Min:</strong> {analytics.pattern_analysis.min} CCF</p>
              <p><strong>Max:</strong> {analytics.pattern_analysis.max} CCF</p>
              <p><strong>Total:</strong> {analytics.pattern_analysis.total} CCF</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analytics;
