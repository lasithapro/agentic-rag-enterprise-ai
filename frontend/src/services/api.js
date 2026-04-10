import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.debug(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(new Error(message));
  }
);

export const documentsApi = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  ingestUrl: async (url) => {
    const response = await apiClient.post('/documents/ingest-url', { url });
    return response.data;
  },

  list: async () => {
    const response = await apiClient.get('/documents');
    return response.data;
  },

  delete: async (documentId) => {
    const response = await apiClient.delete(`/documents/${documentId}`);
    return response.data;
  },
};

export const queryApi = {
  query: async (query, sessionId = null, topK = 5, documentIds = null) => {
    const response = await apiClient.post('/query', {
      query,
      session_id: sessionId,
      top_k: topK,
      document_ids: documentIds,
      include_sources: true,
    });
    return response.data;
  },

  getMemory: async (sessionId) => {
    const response = await apiClient.get(`/memory/${sessionId}`);
    return response.data;
  },

  clearMemory: async (sessionId) => {
    const response = await apiClient.delete(`/memory/${sessionId}`);
    return response.data;
  },
};

export const reportsApi = {
  generate: async (documentIds, actionType = 'generate_report', query = null) => {
    const response = await apiClient.post('/reports/generate', {
      document_ids: documentIds,
      action_type: actionType,
      query,
    });
    return response.data;
  },

  compliance: async (documentIds, policyDocumentIds = null, complianceAreas = null) => {
    const response = await apiClient.post('/reports/compliance', {
      document_ids: documentIds,
      policy_document_ids: policyDocumentIds,
      compliance_areas: complianceAreas,
    });
    return response.data;
  },

  summarize: async (documentIds, query = null) => {
    const response = await apiClient.post('/reports/summarize', {
      document_ids: documentIds,
      action_type: 'summarize',
      query,
    });
    return response.data;
  },
};

export const healthApi = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  detailed: async () => {
    const response = await apiClient.get('/health/detailed');
    return response.data;
  },
};

export default apiClient;
