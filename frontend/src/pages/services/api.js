import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (data) => api.post('/auth/register', data),
  getCurrentUser: () => api.get('/auth/me'),
  changePassword: (currentPassword, newPassword) =>
    api.post('/auth/change-password', { current_password: currentPassword, new_password: newPassword }),
};

// Customers API
export const customersAPI = {
  getAll: () => api.get('/customers'),
  getById: (id) => api.get(`/customers/${id}`),
  getUsage: (id, params) => api.get(`/customers/${id}/usage`, { params }),
  getMonthlyUsage: (id) => api.get(`/customers/${id}/usage/monthly`),
  update: (id, data) => api.put(`/customers/${id}`, data),
  create: (data) => api.post('/customers', data),
};

// Bills API
export const billsAPI = {
  getAll: (params) => api.get('/bills', { params }),
  getById: (id) => api.get(`/bills/${id}`),
  generate: (data) => api.post('/bills/generate', data),
  send: (id) => api.post(`/bills/${id}/send`),
  markPaid: (id) => api.post(`/bills/${id}/pay`),
  getSummary: () => api.get('/bills/summary'),
};

// Usage API
export const usageAPI = {
  getAnomalies: (params) => api.get('/usage/anomalies', { params }),
  detectAnomalies: (data) => api.post('/usage/anomalies/detect', data),
  reviewAnomaly: (id, notes) => api.post(`/usage/anomalies/${id}/review`, { notes }),
  getForecast: (customerId, days) => api.get(`/usage/forecast/${customerId}`, { params: { days } }),
  getForecastedBill: (customerId, month, year) =>
    api.get(`/usage/forecast/${customerId}/bill`, { params: { month, year } }),
  getAnalytics: (customerId) => api.get(`/usage/analytics/${customerId}`),
  uploadData: (records) => api.post('/usage/upload', { records }),
};

export default api;
