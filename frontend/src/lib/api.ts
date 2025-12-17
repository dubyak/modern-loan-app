/**
 * API Client for Modern Loan App
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Methods

export const authAPI = {
  register: (data: { phone: string; password: string; first_name?: string; last_name?: string }) =>
    api.post('/api/auth/register', data),

  login: (data: { phone: string; password: string }) =>
    api.post('/api/auth/login', data),

  sendOTP: (phone: string) =>
    api.post('/api/auth/send-otp', { phone }),

  verifyOTP: (phone: string, code: string) =>
    api.post('/api/auth/verify-otp', { phone, code }),
};

export const usersAPI = {
  getCurrentUser: () => api.get('/api/users/me'),

  updateUser: (data: { first_name?: string; last_name?: string }) =>
    api.put('/api/users/me', data),

  getProfile: () => api.get('/api/users/me/profile'),

  updateProfile: (data: any) => api.put('/api/users/me/profile', data),
};

export const loansAPI = {
  calculate: (data: { amount: number; interest_rate?: number; tenure_days?: number }) =>
    api.post('/api/loans/calculate', data),

  create: (data: { amount: number; interest_rate?: number; tenure_days?: number; ai_decision?: string; ai_confidence?: number }) =>
    api.post('/api/loans', data),

  getLoans: () => api.get('/api/loans'),

  getLoan: (id: string) => api.get(`/api/loans/${id}`),

  acceptLoan: (id: string) => api.post(`/api/loans/${id}/accept`),

  updateStatus: (id: string, data: { status: string; ai_decision?: string; ai_confidence?: number }) =>
    api.put(`/api/loans/${id}/status`, data),
};

export const transactionsAPI = {
  getTransactions: (loanId?: string) =>
    api.get('/api/transactions', { params: { loan_id: loanId } }),

  getTransaction: (id: string) => api.get(`/api/transactions/${id}`),
};

export const aiAPI = {
  chat: (data: { message: string; thread_id?: string }) =>
    api.post('/api/ai/chat', data),

  getThread: () => api.get('/api/ai/thread'),

  getHistory: () => api.get('/api/ai/thread/history'),
};

export const documentsAPI = {
  upload: (file: File, type: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', type);

    return api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getDocuments: (type?: string) =>
    api.get('/api/documents', { params: { document_type: type } }),

  getDocument: (id: string) => api.get(`/api/documents/${id}`),

  deleteDocument: (id: string) => api.delete(`/api/documents/${id}`),
};

export const adminAPI = {
  getUsers: (params?: { page?: number; page_size?: number; role?: string }) =>
    api.get('/api/admin/users', { params }),

  getUser: (id: string) => api.get(`/api/admin/users/${id}`),

  getUserProfile: (id: string) => api.get(`/api/admin/users/${id}/profile`),

  getLoans: (params?: { page?: number; page_size?: number; status?: string; user_id?: string }) =>
    api.get('/api/admin/loans', { params }),

  getStats: () => api.get('/api/admin/stats'),

  updateUserStatus: (id: string, status: string) =>
    api.put(`/api/admin/users/${id}/status`, { status }),
};

export default api;
