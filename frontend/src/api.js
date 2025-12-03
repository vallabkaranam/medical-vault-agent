import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Generate a random session ID if one doesn't exist
const getSessionId = () => {
  let sessionId = localStorage.getItem('mv_session_id');
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('mv_session_id', sessionId);
  }
  return sessionId;
};

export const api = {
  uploadRecord: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', getSessionId());

    const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  standardizeRecord: async (recordId, standard = 'us_cdc') => {
    const response = await axios.post(`${API_BASE_URL}/standardize/${standard}`, {
      record_id: recordId
    });
    return response.data;
  },

  getSessionRecords: async () => {
    const response = await axios.get(`${API_BASE_URL}/records/${getSessionId()}`);
    return response.data;
  },

  async generateSessionReport(standard) {
    const sessionId = getSessionId(); // Changed from this.getSessionId() to getSessionId()
    const response = await axios.post(`${API_BASE_URL}/report/${standard}`, { // Changed from API_URL to API_BASE_URL
      session_id: sessionId
    });
    return response.data;
  }
};

