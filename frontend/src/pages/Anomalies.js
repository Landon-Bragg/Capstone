import React, { useState, useEffect } from 'react';
import { usageAPI } from '../services/api';

function Anomalies({ user }) {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadAnomalies();
  }, []);

  const loadAnomalies = async () => {
    try {
      const response = await usageAPI.getAnomalies({ reviewed: false });
      setAnomalies(response.data);
    } catch (error) {
      console.error('Error loading anomalies:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDetect = async () => {
    setDetecting(true);
    setMessage(null);
    try {
      const response = await usageAPI.detectAnomalies();
      setMessage({ type: 'success', text: response.data.message });
      loadAnomalies();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to detect anomalies' });
    } finally {
      setDetecting(false);
    }
  };

  const handleReview = async (anomalyId) => {
    try {
      await usageAPI.reviewAnomaly(anomalyId, 'Reviewed by ' + user.email);
      setMessage({ type: 'success', text: 'Anomaly marked as reviewed' });
      loadAnomalies();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to review anomaly' });
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <div className="flex-between mb-3">
        <h1>Water Usage Anomalies</h1>
        <button onClick={handleDetect} className="btn btn-primary" disabled={detecting}>
          {detecting ? 'Detecting...' : 'Detect New Anomalies'}
        </button>
      </div>

      {message && (
        <div className={`alert alert-${message.type}`}>{message.text}</div>
      )}

      <div className="alert alert-info">
        <strong>Detection Method:</strong> Statistical analysis using 2 standard deviations above customer average usage.
      </div>

      <div className="card">
        {anomalies.length > 0 ? (
          <table className="table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Date</th>
                <th>Usage (CCF)</th>
                <th>Avg Usage</th>
                <th>Deviation</th>
                <th>Σ Value</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {anomalies.map((anomaly) => (
                <tr key={anomaly.id}>
                  <td>{anomaly.customer_name}</td>
                  <td>{anomaly.date}</td>
                  <td>
                    <span className="badge badge-danger">{anomaly.usage_ccf.toFixed(2)}</span>
                  </td>
                  <td>{anomaly.average_usage.toFixed(2)}</td>
                  <td>{((anomaly.usage_ccf - anomaly.average_usage) / anomaly.average_usage * 100).toFixed(1)}%</td>
                  <td>{anomaly.sigma_value.toFixed(2)}σ</td>
                  <td>
                    <button onClick={() => handleReview(anomaly.id)} className="btn btn-success" style={{ padding: '0.25rem 0.75rem' }}>
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No pending anomalies detected.</p>
        )}
      </div>
    </div>
  );
}

export default Anomalies;
