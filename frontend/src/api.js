import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchDisputes = () => api.get('/disputes');
export const fetchDisputeById = (id) => api.get(`/disputes/${id}`);
export const triggerInvestigation = (id) => api.post(`/disputes/${id}/investigate`);
export const fetchEvidence = (id) => api.get(`/disputes/${id}/evidence`);
export const fetchTimeline = (id) => api.get(`/disputes/${id}/timeline`);
export const fetchAuditEvents = (id) => api.get(`/disputes/${id}/audit`);
export const approveDispute = (id, notes) => api.post(`/disputes/${id}/approve`, { notes });
export const rejectDispute = (id, notes) => api.post(`/disputes/${id}/reject`, { notes });
export const triggerDemoFailure = (dispute_id) => api.post('/demo/failure', { dispute_id });
export const fetchEvaluationSummary = () => api.get('/evaluation/summary');

export default api;
