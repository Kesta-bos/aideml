/**
 * Zustand store for configuration management
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import {
  ConfigSchema,
  ConfigValidationResult,
  Profile,
  Template,
  ModelInfo,
  ConfigCategory,
  ConfigDiff,
} from '@/types/config';
import configAPIService from '@/services/configAPI';

interface ConfigState {
  // Current configuration
  currentConfig: ConfigSchema | null;
  
  // Profiles
  profiles: Profile[];
  activeProfile: Profile | null;
  
  // Templates
  templates: Template[];
  
  // Models
  availableModels: ModelInfo[];
  modelsByProvider: Record<string, ModelInfo[]>;
  
  // UI state
  loading: boolean;
  saving: boolean;
  validating: boolean;
  
  // Validation
  validation: ConfigValidationResult | null;
  fieldValidations: Record<string, ConfigValidationResult>;
  
  // History and changes
  unsavedChanges: boolean;
  changeHistory: ConfigDiff[];
  
  // Error handling
  error: string | null;
  lastError: Error | null;
}

interface ConfigActions {
  // Configuration actions
  loadCurrentConfig: () => Promise<void>;
  updateConfig: (updates: Partial<ConfigSchema>) => Promise<void>;
  updateConfigByCategory: (category: ConfigCategory, updates: Record<string, any>) => Promise<void>;
  validateConfig: () => Promise<void>;
  validateField: (field: string, value: any) => Promise<void>;
  resetToDefaults: () => Promise<void>;
  exportConfig: (format: 'yaml' | 'json', includeSensitive?: boolean) => Promise<string>;
  importConfig: (configData: string, merge?: boolean) => Promise<void>;
  
  // Profile actions
  loadProfiles: () => Promise<void>;
  loadActiveProfile: () => Promise<void>;
  createProfile: (name: string, description: string, category: string) => Promise<Profile>;
  updateProfile: (id: string, updates: Partial<Profile>) => Promise<void>;
  deleteProfile: (id: string) => Promise<void>;
  activateProfile: (id: string) => Promise<void>;
  duplicateProfile: (id: string, newName: string) => Promise<Profile>;
  
  // Template actions
  loadTemplates: () => Promise<void>;
  applyTemplate: (templateName: string) => Promise<void>;
  createProfileFromTemplate: (templateName: string, profileName: string, description?: string) => Promise<Profile>;
  
  // Model actions
  loadAvailableModels: () => Promise<void>;
  loadModelsByProvider: (provider: string) => Promise<void>;
  checkModelCompatibility: (provider: string, model: string, apiKey: string) => Promise<boolean>;
  
  // UI actions
  clearError: () => void;
  setUnsavedChanges: (hasChanges: boolean) => void;
  discardChanges: () => Promise<void>;
  
  // Utility actions
  reset: () => void;
}

type ConfigStore = ConfigState & ConfigActions;

const initialState: ConfigState = {
  currentConfig: null,
  profiles: [],
  activeProfile: null,
  templates: [],
  availableModels: [],
  modelsByProvider: {},
  loading: false,
  saving: false,
  validating: false,
  validation: null,
  fieldValidations: {},
  unsavedChanges: false,
  changeHistory: [],
  error: null,
  lastError: null,
};

export const useConfigStore = create<ConfigStore>()(
  devtools(
    subscribeWithSelector(
      immer((set, get) => ({
        ...initialState,

        // Configuration actions
        loadCurrentConfig: async () => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const config = await configAPIService.config.getCurrentConfig();
            set((state) => {
              state.currentConfig = config;
              state.loading = false;
              state.unsavedChanges = false;
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to load configuration';
              state.lastError = error as Error;
              state.loading = false;
            });
            throw error;
          }
        },

        updateConfig: async (updates: Partial<ConfigSchema>) => {
          set((state) => {
            state.saving = true;
            state.error = null;
          });

          try {
            const updatedConfig = await configAPIService.config.updateConfig({
              config: updates,
            });
            
            set((state) => {
              state.currentConfig = updatedConfig;
              state.saving = false;
              state.unsavedChanges = false;
            });

            // Validate after update
            get().validateConfig();
          } catch (error) {
            set((state) => {
              state.error = 'Failed to update configuration';
              state.lastError = error as Error;
              state.saving = false;
            });
            throw error;
          }
        },

        updateConfigByCategory: async (category: ConfigCategory, updates: Record<string, any>) => {
          set((state) => {
            state.saving = true;
            state.error = null;
          });

          try {
            const updatedConfig = await configAPIService.config.updateConfigByCategory(category, updates);
            
            set((state) => {
              state.currentConfig = updatedConfig;
              state.saving = false;
              state.unsavedChanges = false;
            });

            // Validate after update
            get().validateConfig();
          } catch (error) {
            set((state) => {
              state.error = 'Failed to update configuration';
              state.lastError = error as Error;
              state.saving = false;
            });
            throw error;
          }
        },

        validateConfig: async () => {
          set((state) => {
            state.validating = true;
          });

          try {
            const validation = await configAPIService.config.validateConfig(get().currentConfig || undefined);
            
            set((state) => {
              state.validation = validation;
              state.validating = false;
            });
          } catch (error) {
            set((state) => {
              state.validating = false;
              state.lastError = error as Error;
            });
          }
        },

        validateField: async (field: string, value: any) => {
          try {
            const validation = await configAPIService.config.validateField(field, value);
            
            set((state) => {
              state.fieldValidations[field] = validation;
            });
          } catch (error) {
            console.error('Field validation error:', error);
          }
        },

        resetToDefaults: async () => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const defaultConfig = await configAPIService.config.resetToDefaults();
            
            set((state) => {
              state.currentConfig = defaultConfig;
              state.loading = false;
              state.unsavedChanges = false;
              state.validation = null;
              state.fieldValidations = {};
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to reset configuration';
              state.lastError = error as Error;
              state.loading = false;
            });
            throw error;
          }
        },

        exportConfig: async (format: 'yaml' | 'json', includeSensitive = false) => {
          try {
            return await configAPIService.config.exportConfig({
              format: format as any,
              include_sensitive: includeSensitive,
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to export configuration';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        importConfig: async (configData: string, merge = true) => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const updatedConfig = await configAPIService.config.importConfig({
              config_data: configData,
              merge,
              validate_only: false,
            });
            
            set((state) => {
              state.currentConfig = updatedConfig;
              state.loading = false;
              state.unsavedChanges = false;
            });

            // Validate after import
            get().validateConfig();
          } catch (error) {
            set((state) => {
              state.error = 'Failed to import configuration';
              state.lastError = error as Error;
              state.loading = false;
            });
            throw error;
          }
        },

        // Profile actions
        loadProfiles: async () => {
          try {
            const profiles = await configAPIService.profile.getProfiles();
            set((state) => {
              state.profiles = profiles;
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to load profiles';
              state.lastError = error as Error;
            });
          }
        },

        loadActiveProfile: async () => {
          try {
            const activeProfile = await configAPIService.profile.getActiveProfile();
            set((state) => {
              state.activeProfile = activeProfile;
            });
          } catch (error) {
            // Active profile might not exist, which is okay
            set((state) => {
              state.activeProfile = null;
            });
          }
        },

        createProfile: async (name: string, description: string, category: string) => {
          const currentConfig = get().currentConfig;
          if (!currentConfig) {
            throw new Error('No current configuration to save as profile');
          }

          try {
            const profile = await configAPIService.profile.createProfile({
              name,
              description,
              category,
              config: currentConfig,
            });

            set((state) => {
              state.profiles.push(profile);
            });

            return profile;
          } catch (error) {
            set((state) => {
              state.error = 'Failed to create profile';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        updateProfile: async (id: string, updates: Partial<Profile>) => {
          try {
            const updatedProfile = await configAPIService.profile.updateProfile(id, updates);
            
            set((state) => {
              const index = state.profiles.findIndex(p => p.id === id);
              if (index >= 0) {
                state.profiles[index] = updatedProfile;
              }
              if (state.activeProfile?.id === id) {
                state.activeProfile = updatedProfile;
              }
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to update profile';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        deleteProfile: async (id: string) => {
          try {
            await configAPIService.profile.deleteProfile(id);
            
            set((state) => {
              state.profiles = state.profiles.filter(p => p.id !== id);
              if (state.activeProfile?.id === id) {
                state.activeProfile = null;
              }
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to delete profile';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        activateProfile: async (id: string) => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const config = await configAPIService.profile.activateProfile(id);
            const profile = get().profiles.find(p => p.id === id);
            
            set((state) => {
              state.currentConfig = config;
              state.activeProfile = profile || null;
              state.loading = false;
              state.unsavedChanges = false;
            });

            // Validate after activation
            get().validateConfig();
          } catch (error) {
            set((state) => {
              state.error = 'Failed to activate profile';
              state.lastError = error as Error;
              state.loading = false;
            });
            throw error;
          }
        },

        duplicateProfile: async (id: string, newName: string) => {
          try {
            const duplicatedProfile = await configAPIService.profile.duplicateProfile(id, newName);
            
            set((state) => {
              state.profiles.push(duplicatedProfile);
            });

            return duplicatedProfile;
          } catch (error) {
            set((state) => {
              state.error = 'Failed to duplicate profile';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        // Template actions
        loadTemplates: async () => {
          try {
            const templates = await configAPIService.template.getTemplates();
            set((state) => {
              state.templates = templates;
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to load templates';
              state.lastError = error as Error;
            });
          }
        },

        applyTemplate: async (templateName: string) => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const config = await configAPIService.template.applyTemplate(templateName);
            
            set((state) => {
              state.currentConfig = config;
              state.loading = false;
              state.unsavedChanges = true;
            });

            // Validate after applying template
            get().validateConfig();
          } catch (error) {
            set((state) => {
              state.error = 'Failed to apply template';
              state.lastError = error as Error;
              state.loading = false;
            });
            throw error;
          }
        },

        createProfileFromTemplate: async (templateName: string, profileName: string, description?: string) => {
          try {
            const profile = await configAPIService.template.createProfileFromTemplate(
              templateName,
              profileName,
              description
            );
            
            set((state) => {
              state.profiles.push(profile);
            });

            return profile;
          } catch (error) {
            set((state) => {
              state.error = 'Failed to create profile from template';
              state.lastError = error as Error;
            });
            throw error;
          }
        },

        // Model actions
        loadAvailableModels: async () => {
          try {
            const models = await configAPIService.model.getAvailableModels();
            set((state) => {
              state.availableModels = models;
            });
          } catch (error) {
            set((state) => {
              state.error = 'Failed to load available models';
              state.lastError = error as Error;
            });
          }
        },

        loadModelsByProvider: async (provider: string) => {
          try {
            const models = await configAPIService.model.getModelsByProvider(provider);
            set((state) => {
              state.modelsByProvider[provider] = models;
            });
          } catch (error) {
            console.error('Failed to load models for provider:', provider, error);
          }
        },

        checkModelCompatibility: async (provider: string, model: string, apiKey: string) => {
          try {
            const result = await configAPIService.model.checkModelCompatibility({
              provider: provider as any,
              model,
              api_key: apiKey,
            });
            return result.compatible;
          } catch (error) {
            console.error('Model compatibility check failed:', error);
            return false;
          }
        },

        // UI actions
        clearError: () => {
          set((state) => {
            state.error = null;
            state.lastError = null;
          });
        },

        setUnsavedChanges: (hasChanges: boolean) => {
          set((state) => {
            state.unsavedChanges = hasChanges;
          });
        },

        discardChanges: async () => {
          await get().loadCurrentConfig();
        },

        reset: () => {
          set(initialState);
        },
      }))
    ),
    {
      name: 'aide-config-store',
    }
  )
);

// Selectors for commonly used state combinations
export const useConfigValidation = () => useConfigStore((state) => ({
  validation: state.validation,
  fieldValidations: state.fieldValidations,
  validating: state.validating,
}));

export const useConfigProfiles = () => useConfigStore((state) => ({
  profiles: state.profiles,
  activeProfile: state.activeProfile,
}));

export const useConfigTemplates = () => useConfigStore((state) => ({
  templates: state.templates,
}));

export const useConfigModels = () => useConfigStore((state) => ({
  availableModels: state.availableModels,
  modelsByProvider: state.modelsByProvider,
}));

export const useConfigUI = () => useConfigStore((state) => ({
  loading: state.loading,
  saving: state.saving,
  error: state.error,
  unsavedChanges: state.unsavedChanges,
}));