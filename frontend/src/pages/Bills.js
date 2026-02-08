import React, { useState, useEffect } from 'react';
import { billsAPI } from '../services/api';

function Bills({ user }) {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadBills();
  }, []);

  const loadBills = async () => {
    try {
      const response = await billsAPI.getAll();
      setBills(response.data);
    } catch (error) {
      console.error('Error loading bills:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBills = async () => {
    setGenerating(true);
    setMessage(null);
    try {
      const response = await billsAPI.generate();
      setMessage({ type: 'success', text: response.data.message });
      loadBills();
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.error || 'Failed to generate bills' });
    } finally {
      setGenerating(false);
    }
  };

  const handleSendBill = async (billId) => {
    try {
      await billsAPI.send(billId);
      setMessage({ type: 'success', text: 'Bill sent successfully' });
      loadBills();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to send bill' });
    }
  };

  const handleMarkPaid = async (billId) => {
    try {
      await billsAPI.markPaid(billId);
      setMessage({ type: 'success', text: 'Bill marked as paid' });
      loadBills();
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to mark bill as paid' });
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <div className="flex-between mb-3">
        <h1>Bills</h1>
        {user.role === 'billing' || user.role === 'operations' ? (
          <button onClick={handleGenerateBills} className="btn btn-primary" disabled={generating}>
            {generating ? 'Generating...' : 'Generate Bills'}
          </button>
        ) : null}
      </div>

      {message && (
        <div className={`alert alert-${message.type}`}>{message.text}</div>
      )}

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Customer</th>
              <th>Period</th>
              <th>Usage (CCF)</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {bills.map((bill) => (
              <tr key={bill.id}>
                <td>{bill.customer_name}</td>
                <td>{bill.billing_period_start} to {bill.billing_period_end}</td>
                <td>{bill.total_usage.toFixed(2)}</td>
                <td>${bill.total_amount.toFixed(2)}</td>
                <td>
                  <span className={`badge badge-${bill.status === 'paid' ? 'success' : bill.status === 'sent' ? 'warning' : 'info'}`}>
                    {bill.status}
                  </span>
                </td>
                <td>
                  {user.role !== 'customer' && bill.status === 'pending' && (
                    <button onClick={() => handleSendBill(bill.id)} className="btn btn-primary" style={{ padding: '0.25rem 0.75rem', marginRight: '0.5rem' }}>
                      Send
                    </button>
                  )}
                  {bill.status === 'sent' && (
                    <button onClick={() => handleMarkPaid(bill.id)} className="btn btn-success" style={{ padding: '0.25rem 0.75rem' }}>
                      Mark Paid
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Bills;
