import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ApiKeyConfig } from '@/types';

interface SettingsState {
  // API Keys
  apiKeys: ApiKeyConfig;
  
  // UI Preferences
  theme: 'light' | 'dark' | 'auto';
  language: string;
  autoSave: boolean;
  
  // Experiment Defaults
  defaultSteps: number;
  defaultEvalCriteria: string;
  
  // Actions
  setApiKey: (provider: keyof ApiKeyConfig, key: string) => void;
  clearApiKey: (provider: keyof ApiKeyConfig) => void;
  clearAllApiKeys: () => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
  setLanguage: (language: string) => void;
  setAutoSave: (autoSave: boolean) => void;
  setDefaultSteps: (steps: number) => void;
  setDefaultEvalCriteria: (criteria: string) => void;
  
  // Getters
  hasValidApiKey: () => boolean;
  getApiKeyForProvider: (provider: keyof ApiKeyConfig) => string | undefined;
}

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        apiKeys: {
          openaiKey: '',
          anthropicKey: '',
          openrouterKey: '',
        },
        theme: 'light',
        language: 'en',
        autoSave: true,
        defaultSteps: 10,
        defaultEvalCriteria: '',

        // API Key actions
        setApiKey: (provider, key) =>
          set((state) => ({
            apiKeys: {
              ...state.apiKeys,
              [provider]: key,
            },
          }), false, `setApiKey-${provider}`),

        clearApiKey: (provider) =>
          set((state) => ({
            apiKeys: {
              ...state.apiKeys,
              [provider]: '',
            },
          }), false, `clearApiKey-${provider}`),

        clearAllApiKeys: () =>
          set({
            apiKeys: {
              openaiKey: '',
              anthropicKey: '',
              openrouterKey: '',
            },
          }, false, 'clearAllApiKeys'),

        // UI Preference actions
        setTheme: (theme) => set({ theme }, false, 'setTheme'),
        setLanguage: (language) => set({ language }, false, 'setLanguage'),
        setAutoSave: (autoSave) => set({ autoSave }, false, 'setAutoSave'),

        // Experiment default actions
        setDefaultSteps: (steps) => set({ defaultSteps: steps }, false, 'setDefaultSteps'),
        setDefaultEvalCriteria: (criteria) => set({ defaultEvalCriteria: criteria }, false, 'setDefaultEvalCriteria'),

        // Getters
        hasValidApiKey: () => {
          const { apiKeys } = get();
          return !!(apiKeys.openaiKey || apiKeys.anthropicKey || apiKeys.openrouterKey);
        },

        getApiKeyForProvider: (provider) => {
          const { apiKeys } = get();
          return apiKeys[provider];
        },
      }),
      {
        name: 'aide-settings',
        // Only persist certain fields
        partialize: (state) => ({
          apiKeys: state.apiKeys,
          theme: state.theme,
          language: state.language,
          autoSave: state.autoSave,
          defaultSteps: state.defaultSteps,
          defaultEvalCriteria: state.defaultEvalCriteria,
        }),
      }
    ),
    {
      name: 'settings-store',
    }
  )
);

// Selectors for common combinations
export const useApiKeys = () => {
  const { apiKeys, setApiKey, clearApiKey, clearAllApiKeys, hasValidApiKey } = useSettingsStore();
  return { apiKeys, setApiKey, clearApiKey, clearAllApiKeys, hasValidApiKey };
};

export const useThemeSettings = () => {
  const { theme, setTheme } = useSettingsStore();
  return { theme, setTheme };
};

export const useExperimentDefaults = () => {
  const { defaultSteps, defaultEvalCriteria, setDefaultSteps, setDefaultEvalCriteria } = useSettingsStore();
  return { defaultSteps, defaultEvalCriteria, setDefaultSteps, setDefaultEvalCriteria };
};
