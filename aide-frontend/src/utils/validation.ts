/**
 * Validation utilities
 */

import { appConfig } from '@/config/app';

export function validateFileType(file: File): boolean {
  const extension = file.name.split('.').pop()?.toLowerCase();
  return extension ? appConfig.upload.allowedTypes.includes(extension) : false;
}

export function validateFileSize(file: File): boolean {
  return file.size <= appConfig.upload.maxSize;
}

export function validateExperimentName(name: string): string | null {
  if (!name || name.trim().length === 0) {
    return 'Experiment name is required';
  }
  if (name.length > 100) {
    return 'Experiment name must be less than 100 characters';
  }
  return null;
}

export function validateGoal(goal: string): string | null {
  if (!goal || goal.trim().length === 0) {
    return 'Goal is required';
  }
  if (goal.length > 1000) {
    return 'Goal must be less than 1000 characters';
  }
  return null;
}

export function validateSteps(steps: number): string | null {
  if (steps < 1) {
    return 'Number of steps must be at least 1';
  }
  if (steps > appConfig.experiment.maxSteps) {
    return `Number of steps cannot exceed ${appConfig.experiment.maxSteps}`;
  }
  return null;
}

export function validateApiKey(apiKey: string, provider: string): string | null {
  if (!apiKey || apiKey.trim().length === 0) {
    return `${provider} API key is required`;
  }
  
  // Basic format validation
  switch (provider.toLowerCase()) {
    case 'openai':
      if (!apiKey.startsWith('sk-')) {
        return 'OpenAI API key should start with "sk-"';
      }
      break;
    case 'anthropic':
      if (!apiKey.startsWith('sk-ant-')) {
        return 'Anthropic API key should start with "sk-ant-"';
      }
      break;
    case 'openrouter':
      if (!apiKey.startsWith('sk-or-')) {
        return 'OpenRouter API key should start with "sk-or-"';
      }
      break;
  }
  
  return null;
}

export interface FileValidationResult {
  isValid: boolean;
  errors: string[];
}

export function validateFiles(files: File[]): FileValidationResult {
  const errors: string[] = [];
  
  if (files.length === 0) {
    errors.push('At least one file is required');
  }
  
  files.forEach((file, index) => {
    if (!validateFileType(file)) {
      errors.push(`File ${index + 1} (${file.name}): Invalid file type. Allowed types: ${appConfig.upload.allowedTypes.join(', ')}`);
    }
    
    if (!validateFileSize(file)) {
      errors.push(`File ${index + 1} (${file.name}): File too large. Maximum size: ${Math.round(appConfig.upload.maxSize / (1024 * 1024))}MB`);
    }
  });
  
  return {
    isValid: errors.length === 0,
    errors,
  };
}
