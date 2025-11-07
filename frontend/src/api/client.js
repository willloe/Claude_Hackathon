/**
 * Axios API client configuration
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
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
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// API functions
export const authAPI = {
  register: (data) => apiClient.post('/api/auth/register', data),
  login: (data) => apiClient.post('/api/auth/login', data),
  getMe: () => apiClient.get('/api/auth/me'),
};

export const coursesAPI = {
  create: (data) => apiClient.post('/api/courses', data),
  list: () => apiClient.get('/api/courses'),
  get: (id) => apiClient.get(`/api/courses/${id}`),
  update: (id, data) => apiClient.put(`/api/courses/${id}`, data),
  delete: (id) => apiClient.delete(`/api/courses/${id}`),
};

export const materialsAPI = {
  upload: (courseId, formData) =>
    apiClient.post(`/api/courses/${courseId}/materials`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  list: (courseId) => apiClient.get(`/api/courses/${courseId}/materials`),
  delete: (materialId) => apiClient.delete(`/api/materials/${materialId}`),
};

export const policiesAPI = {
  update: (courseId, data) =>
    apiClient.put(`/api/courses/${courseId}/policies`, data),
  get: (courseId) => apiClient.get(`/api/courses/${courseId}/policies`),
};

export const qaAPI = {
  ask: (courseId, question) =>
    apiClient.post(`/api/courses/${courseId}/ask`, { question }),
  getLogs: (courseId) => apiClient.get(`/api/courses/${courseId}/qa-logs`),
};

export const analyticsAPI = {
  get: (courseId) => apiClient.get(`/api/courses/${courseId}/analytics`),
};
