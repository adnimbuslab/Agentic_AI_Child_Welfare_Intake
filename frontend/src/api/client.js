import axios from 'axios';

const api = axios.create({ baseURL: '' });

export function createSession(reporterType) {
  return api.post('/intake/session', { reporterType });
}

export function submitMessage(caseId, messageText, attachmentIds) {
  return api.post('/intake/message', { caseId, messageText, attachmentIds });
}

export function uploadDocument(caseId, file, documentCategory) {
  const form = new FormData();
  form.append('caseId', caseId);
  form.append('file', file);
  form.append('documentCategory', documentCategory || 'other');
  return api.post('/intake/upload', form);
}

export function listCases(params) {
  return api.get('/cases', { params });
}

export function getCaseSummary(caseId) {
  return api.get(`/cases/${caseId}`);
}

export function getCaseExplanation(caseId) {
  return api.get(`/cases/${caseId}/summary`);
}

export function submitHumanReview(caseId, data) {
  return api.post(`/cases/${caseId}/human-review`, data);
}
