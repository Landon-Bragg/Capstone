import React, { useState, useEffect } from 'react';
import { customersAPI } from '../services/api';

function Customers({ user }) {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await customersAPI.getAll();
      setCustomers(response.data);
    } catch (error) {
      console.error('Error loading customers:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner"></div></div>;
  }

  return (
    <div>
      <h1>Customers</h1>
      
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Address</th>
              <th>Type</th>
              <th>Cycle</th>
              <th>Avg Usage</th>
              <th>Total Bills</th>
              <th>Anomalies</th>
            </tr>
          </thead>
          <tbody>
            {customers.map((customer) => (
              <tr key={customer.id}>
                <td>{customer.name}</td>
                <td>{customer.address}</td>
                <td>{customer.customer_type}</td>
                <td>{customer.cycle_number}</td>
                <td>{customer.stats?.avg_daily_usage?.toFixed(2) || 0} CCF</td>
                <td>{customer.stats?.total_bills || 0}</td>
                <td>
                  {customer.stats?.anomaly_count > 0 && (
                    <span className="badge badge-warning">{customer.stats.anomaly_count}</span>
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

export default Customers;
