import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Session APIs
export const sessionAPI = {
  getSession: async (sessionId: string) => {
    const response = await api.get(`/session/${sessionId}`);
    return response.data;
  },

  updateMetadata: async (sessionId: string, metadata: any) => {
    const response = await api.post(`/session/${sessionId}/metadata`, metadata);
    return response.data;
  },
};

// Design APIs
export const designAPI = {
  saveDesign: async (sessionId: string, elements: any[]) => {
    const response = await api.post(`/design/${sessionId}/save`, { elements });
    return response.data;
  },

  loadDesign: async (sessionId: string) => {
    const response = await api.get(`/design/${sessionId}`);
    return response.data;
  },

  addRoad: async (sessionId: string, road: any) => {
    const response = await api.post(`/design/${sessionId}/road`, road);
    return response.data;
  },

  addBuilding: async (sessionId: string, building: any) => {
    const response = await api.post(`/design/${sessionId}/building`, building);
    return response.data;
  },

  updateElement: async (sessionId: string, elementId: string, updates: any) => {
    const response = await api.put(`/design/${sessionId}/element/${elementId}`, updates);
    return response.data;
  },

  deleteElement: async (sessionId: string, elementId: string) => {
    const response = await api.delete(`/design/${sessionId}/element/${elementId}`);
    return response.data;
  },
};

// Chat APIs
export const chatAPI = {
  sendMessage: async (sessionId: string, message: string) => {
    const response = await api.post(`/chat/${sessionId}`, { message });
    return response.data;
  },

  getChatHistory: async (sessionId: string) => {
    const response = await api.get(`/chat/${sessionId}/history`);
    return response.data;
  },
};

// Export APIs
export const exportAPI = {
  exportDXF: async (sessionId: string) => {
    const response = await api.get(`/export/${sessionId}/dxf`, {
      responseType: 'blob',
    });
    return response.data;
  },

  exportGeoJSON: async (sessionId: string) => {
    const response = await api.get(`/export/${sessionId}/geojson`);
    return response.data;
  },
};

export default api;
