import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

const apiService = {
  getDbStatus: async () => {
    try {
      const response = await apiClient.get('/db/status');
      return response.data;
    } catch (error) {
      console.error("Error fetching DB status:", error);
      throw error.response ? error.response.data : new Error('Network error or API is down');
    }
  },
  getSchemas: async () => {
    try {
      const response = await apiClient.get('/db/schemas');
      return response.data;
    } catch (error) {
      console.error("Error fetching schemas:", error);
      throw error.response ? error.response.data : new Error('Network error or API is down');
    }
  },
  getSchemaDetails: async (schemaName) => {
    try {
      const response = await apiClient.get(`/db/schema/${schemaName}/details`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching details for schema ${schemaName}:`, error);
      throw error.response ? error.response.data : new Error('Network error or API is down');
    }
  },
};

export default apiService;
