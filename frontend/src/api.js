import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  /**
   * Upload a vaccination record image.
   * @param {File} file - The image or PDF file to upload.
   * @returns {Promise<Object>} - The upload result with extracted data.
   */
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

  /**
   * Standardize a specific record against a compliance standard.
   * @param {string} recordId - The ID of the record to standardize.
   * @param {string} standard - The compliance standard (e.g., 'us_cdc', 'cornell_tech').
   * @returns {Promise<Object>} - The standardization result.
   */
  standardizeRecord: async (recordId, standard = 'us_cdc') => {
    const response = await axios.post(`${API_BASE_URL}/standardize/${standard}`, {
      record_id: recordId
    });
    return response.data;
  },

  /**
   * Get all records for the current session.
   * @returns {Promise<Array>} - List of uploaded records.
   */
  getSessionRecords: async () => {
    const response = await axios.get(`${API_BASE_URL}/records/${getSessionId()}`);
    return response.data;
  },

  /**
   * Generate an aggregate compliance report for the current session.
   * @param {string} standard - The compliance standard to check against.
   * @returns {Promise<Object>} - The aggregate standardization result.
   */
  async generateSessionReport(standard) {
    const sessionId = getSessionId();
    const response = await axios.post(`${API_BASE_URL}/report/${standard}`, {
      session_id: sessionId
    });
    return response.data;
  }
};

