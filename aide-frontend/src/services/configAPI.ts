/**
 * Configuration management API service
 * Communicates with the AIDE ML backend configuration endpoints
 */

import axios, { AxiosResponse } from 'axios';
import {
  ConfigSchema,
  ConfigUpdateRequest,
  ConfigValidationResult,
  ModelInfo,
  ModelCompatibilityCheck,
  ModelCompatibilityResult,
  ConfigExportRequest,
  ConfigImportRequest,
  ApiResponse,
  Profile,
  ProfileCreateRequest,
  ProfileUpdateRequest,
  Template,
  ConfigCategory,
} from '@/types/config';

// Base API configuration
const API_BASE_URL = process.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Configuration Management
export const configAPI = {
  // Get current configuration
  async getCurrentConfig(): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.get('/config/current');
    return response.data.data!;
  },

  // Update configuration
  async updateConfig(request: ConfigUpdateRequest): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post('/config/update', request);
    return response.data.data!;
  },

  // Validate configuration
  async validateConfig(config?: Partial<ConfigSchema>): Promise<ConfigValidationResult> {
    const response: AxiosResponse<ApiResponse<ConfigValidationResult>> = await api.post('/config/validate', config || {});
    return response.data.data!;
  },

  // Validate specific field
  async validateField(field: string, value: any): Promise<ConfigValidationResult> {
    const response: AxiosResponse<ApiResponse<ConfigValidationResult>> = await api.post('/config/validate-field', {
      field,
      value,
    });
    return response.data.data!;
  },

  // Reset to defaults
  async resetToDefaults(): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post('/config/reset');
    return response.data.data!;
  },

  // Export configuration
  async exportConfig(request: ConfigExportRequest): Promise<string> {
    const response: AxiosResponse<ApiResponse<string>> = await api.post('/config/export', request);
    return response.data.data!;
  },

  // Import configuration
  async importConfig(request: ConfigImportRequest): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post('/config/import', request);
    return response.data.data!;
  },

  // Get configuration by category
  async getConfigByCategory(category: ConfigCategory): Promise<Partial<ConfigSchema>> {
    const response: AxiosResponse<ApiResponse<Partial<ConfigSchema>>> = await api.get(`/config/category/${category}`);
    return response.data.data!;
  },

  // Update configuration by category
  async updateConfigByCategory(category: ConfigCategory, config: Record<string, any>): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post(`/config/category/${category}`, config);
    return response.data.data!;
  },
};

// Model Management
export const modelAPI = {
  // Get available models
  async getAvailableModels(): Promise<ModelInfo[]> {
    const response: AxiosResponse<ApiResponse<ModelInfo[]>> = await api.get('/models');
    return response.data.data!;
  },

  // Get models by provider
  async getModelsByProvider(provider: string): Promise<ModelInfo[]> {
    const response: AxiosResponse<ApiResponse<ModelInfo[]>> = await api.get(`/models/provider/${provider}`);
    return response.data.data!;
  },

  // Check model compatibility
  async checkModelCompatibility(request: ModelCompatibilityCheck): Promise<ModelCompatibilityResult> {
    const response: AxiosResponse<ApiResponse<ModelCompatibilityResult>> = await api.post('/models/compatibility', request);
    return response.data.data!;
  },

  // Get model info
  async getModelInfo(modelName: string): Promise<ModelInfo> {
    const response: AxiosResponse<ApiResponse<ModelInfo>> = await api.get(`/models/${modelName}`);
    return response.data.data!;
  },
};

// Profile Management
export const profileAPI = {
  // Get all profiles
  async getProfiles(): Promise<Profile[]> {
    const response: AxiosResponse<ApiResponse<Profile[]>> = await api.get('/profiles');
    return response.data.data!;
  },

  // Get profile by ID
  async getProfile(id: string): Promise<Profile> {
    const response: AxiosResponse<ApiResponse<Profile>> = await api.get(`/profiles/${id}`);
    return response.data.data!;
  },

  // Create new profile
  async createProfile(request: ProfileCreateRequest): Promise<Profile> {
    const response: AxiosResponse<ApiResponse<Profile>> = await api.post('/profiles', request);
    return response.data.data!;
  },

  // Update profile
  async updateProfile(id: string, request: ProfileUpdateRequest): Promise<Profile> {
    const response: AxiosResponse<ApiResponse<Profile>> = await api.put(`/profiles/${id}`, request);
    return response.data.data!;
  },

  // Delete profile
  async deleteProfile(id: string): Promise<void> {
    await api.delete(`/profiles/${id}`);
  },

  // Activate profile
  async activateProfile(id: string): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post(`/profiles/${id}/activate`);
    return response.data.data!;
  },

  // Duplicate profile
  async duplicateProfile(id: string, name: string): Promise<Profile> {
    const response: AxiosResponse<ApiResponse<Profile>> = await api.post(`/profiles/${id}/duplicate`, { name });
    return response.data.data!;
  },

  // Get active profile
  async getActiveProfile(): Promise<Profile | null> {
    try {
      const response: AxiosResponse<ApiResponse<Profile>> = await api.get('/profiles/active');
      return response.data.data!;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },
};

// Template Management
export const templateAPI = {
  // Get all templates
  async getTemplates(): Promise<Template[]> {
    const response: AxiosResponse<ApiResponse<Template[]>> = await api.get('/templates');
    return response.data.data!;
  },

  // Get template by name
  async getTemplate(name: string): Promise<Template> {
    const response: AxiosResponse<ApiResponse<Template>> = await api.get(`/templates/${name}`);
    return response.data.data!;
  },

  // Apply template
  async applyTemplate(name: string): Promise<ConfigSchema> {
    const response: AxiosResponse<ApiResponse<ConfigSchema>> = await api.post(`/templates/${name}/apply`);
    return response.data.data!;
  },

  // Create profile from template
  async createProfileFromTemplate(templateName: string, profileName: string, description?: string): Promise<Profile> {
    const response: AxiosResponse<ApiResponse<Profile>> = await api.post(`/templates/${templateName}/create-profile`, {
      name: profileName,
      description: description || `Profile created from ${templateName} template`,
    });
    return response.data.data!;
  },
};

// Utility functions
export const configUtils = {
  // Download configuration as file
  async downloadConfig(format: 'yaml' | 'json' = 'yaml', filename?: string): Promise<void> {
    const configData = await configAPI.exportConfig({
      format: format as any,
      include_sensitive: false,
    });

    const blob = new Blob([configData], {
      type: format === 'yaml' ? 'text/yaml' : 'application/json',
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || `aide-config.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  // Upload and import configuration
  async uploadConfig(file: File, merge: boolean = true): Promise<ConfigSchema> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const configData = e.target?.result as string;
          const result = await configAPI.importConfig({
            config_data: configData,
            merge,
            validate_only: false,
          });
          resolve(result);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  },
};

export default {
  config: configAPI,
  model: modelAPI,
  profile: profileAPI,
  template: templateAPI,
  utils: configUtils,
};