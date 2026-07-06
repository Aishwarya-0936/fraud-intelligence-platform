import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const getTransactions = (params = {}) =>
  api.get('/transactions/', { params }).then((res) => res.data);

export const getTransaction = (id) =>
  api.get(`/transactions/${id}`).then((res) => res.data);

export const createTransaction = (payload) =>
  api.post('/transactions/', payload).then((res) => res.data);

export const reviewTransaction = (id, decision, reviewer_notes) =>
  api.post(`/transactions/${id}/review`, { decision, reviewer_notes }).then((res) => res.data);

export default api;