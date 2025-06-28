import axios, { AxiosResponse } from 'axios';
import { 
  ApiResponse, 
  ExperimentConfig, 
  ExperimentCreateRequest, 
  ExperimentResults,
  UploadedFile 
} from '@/types';

// Create axios instance with default config
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    // Handle common error cases
    if (error.response?.status === 404) {
      throw new Error('Resource not found');
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Bad request');
    } else if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please try again.');
    }
    
    throw error;
  }
);

// Experiment API
export const experimentAPI = {
  create: async (request: ExperimentCreateRequest): Promise<ExperimentConfig> => {
    const response: AxiosResponse<ApiResponse<ExperimentConfig>> = await api.post(
      '/api/experiments', 
      request
    );
    return response.data.data!;
  },

  get: async (id: string): Promise<ExperimentConfig> => {
    const response: AxiosResponse<ApiResponse<ExperimentConfig>> = await api.get(
      `/api/experiments/${id}`
    );
    return response.data.data!;
  },

  start: async (id: string): Promise<void> => {
    await api.post(`/api/experiments/${id}/start`);
  },

  stop: async (id: string): Promise<void> => {
    await api.post(`/api/experiments/${id}/stop`);
  },

  getStatus: async (id: string): Promise<any> => {
    const response: AxiosResponse<ApiResponse<any>> = await api.get(
      `/api/experiments/${id}/status`
    );
    return response.data.data!;
  },

  getResults: async (id: string): Promise<ExperimentResults> => {
    const response: AxiosResponse<ApiResponse<ExperimentResults>> = await api.get(
      `/api/experiments/${id}/results`
    );
    return response.data.data!;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/experiments/${id}`);
  },

  list: async (page = 1, limit = 10, status?: string): Promise<any> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
    });
    
    if (status) {
      params.append('status', status);
    }
    
    const response: AxiosResponse<ApiResponse<any>> = await api.get(
      `/api/experiments?${params}`
    );
    return response.data.data!;
  },
};

// File API
export const fileAPI = {
  upload: async (files: FileList | File[]): Promise<UploadedFile[]> => {
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    const response: AxiosResponse<ApiResponse<UploadedFile[]>> = await api.post(
      '/api/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 seconds for file uploads
      }
    );
    
    return response.data.data!;
  },

  getInfo: async (id: string): Promise<UploadedFile> => {
    const response: AxiosResponse<ApiResponse<UploadedFile>> = await api.get(
      `/api/files/${id}`
    );
    return response.data.data!;
  },

  download: async (id: string): Promise<Blob> => {
    const response = await api.get(`/api/files/${id}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/files/${id}`);
  },
};

// Configuration API
export const configAPI = {
  get: async (): Promise<any> => {
    const response: AxiosResponse<ApiResponse<any>> = await api.get('/api/config');
    return response.data.data!;
  },

  validateApiKey: async (provider: string, apiKey: string): Promise<any> => {
    const response: AxiosResponse<ApiResponse<any>> = await api.post(
      '/api/config/validate-api-key',
      { provider, apiKey }
    );
    return response.data.data!;
  },
};

// Example Tasks API
export const exampleTaskAPI = {
  list: async (): Promise<any[]> => {
    const response: AxiosResponse<ApiResponse<any[]>> = await api.get('/api/example-tasks');
    return response.data.data!;
  },

  get: async (taskId: string): Promise<any> => {
    const response: AxiosResponse<ApiResponse<any>> = await api.get(`/api/example-tasks/${taskId}`);
    return response.data.data!;
  },

  downloadFile: async (taskId: string, filename: string): Promise<Blob> => {
    const response = await api.get(`/api/example-tasks/${taskId}/files/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async (): Promise<any> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
