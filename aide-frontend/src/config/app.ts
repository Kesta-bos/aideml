import type { AppConfig } from '@/types';

export const appConfig: AppConfig = {
  api: {
    baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
    wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
    timeout: 30000,
  },
  upload: {
    maxSize: parseInt(import.meta.env.VITE_MAX_UPLOAD_SIZE || '104857600'), // 100MB
    allowedTypes: (import.meta.env.VITE_SUPPORTED_FORMATS || 'csv,json,txt,zip,xlsx,md').split(','),
  },
  experiment: {
    maxSteps: 50,
    defaultSteps: 10,
  },
};

export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

export const appInfo = {
  name: import.meta.env.VITE_APP_NAME || 'AIDE ML',
  version: import.meta.env.VITE_APP_VERSION || '2.0.0',
};
