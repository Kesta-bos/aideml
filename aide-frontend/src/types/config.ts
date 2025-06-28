/**
 * Configuration management types for AIDE ML
 * Based on backend config_models.py
 */

export enum ModelProvider {
  OPENAI = 'openai',
  ANTHROPIC = 'anthropic',
  OPENROUTER = 'openrouter',
}

export enum ConfigCategory {
  PROJECT = 'project',
  AGENT = 'agent',
  EXECUTION = 'execution',
  MODELS = 'models',
  SEARCH = 'search',
  REPORTING = 'reporting',
}

export enum ConfigExportFormat {
  YAML = 'yaml',
  JSON = 'json',
}

export interface StageConfig {
  model: string;
  temp: number;
}

export interface SearchConfig {
  max_debug_depth: number;
  debug_prob: number;
  num_drafts: number;
}

export interface AgentConfig {
  steps: number;
  k_fold_validation: number;
  expose_prediction: boolean;
  data_preview: boolean;
  code: StageConfig;
  feedback: StageConfig;
  search: SearchConfig;
}

export interface ExecConfig {
  timeout: number;
  agent_file_name: string;
  format_tb_ipython: boolean;
}

export interface ConfigSchema {
  // Project settings
  data_dir?: string;
  desc_file?: string;
  goal?: string;
  eval?: string;

  // Directory settings
  log_dir: string;
  workspace_dir: string;

  // Data processing
  preprocess_data: boolean;
  copy_data: boolean;

  // Experiment settings
  exp_name?: string;

  // Component configurations
  exec: ExecConfig;
  generate_report: boolean;
  report: StageConfig;
  agent: AgentConfig;
}

export interface ConfigUpdateRequest {
  category?: ConfigCategory;
  config: Record<string, any>;
}

export interface ConfigValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface ConfigValidationResult {
  valid: boolean;
  errors: ConfigValidationError[];
  warnings: string[];
}

export interface ModelInfo {
  name: string;
  provider: ModelProvider;
  display_name: string;
  description: string;
  supports_function_calling: boolean;
  max_tokens?: number;
  cost_per_1k_tokens?: number;
}

export interface ModelCompatibilityCheck {
  provider: ModelProvider;
  model: string;
  api_key: string;
}

export interface ModelCompatibilityResult {
  compatible: boolean;
  model_available: boolean;
  api_key_valid: boolean;
  message: string;
  estimated_cost?: number;
}

export interface ConfigExportRequest {
  format: ConfigExportFormat;
  include_sensitive: boolean;
}

export interface ConfigImportRequest {
  config_data: string;
  merge: boolean;
  validate_only: boolean;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
  timestamp: string;
}

// Profile Management Types
export interface Profile {
  id: string;
  name: string;
  description: string;
  category: string;
  config: ConfigSchema;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  tags: string[];
}

export interface ProfileCreateRequest {
  name: string;
  description: string;
  category: string;
  config: ConfigSchema;
  tags?: string[];
}

export interface ProfileUpdateRequest {
  name?: string;
  description?: string;
  category?: string;
  config?: Partial<ConfigSchema>;
  tags?: string[];
}

export interface Template {
  name: string;
  display_name: string;
  description: string;
  category: string;
  config: ConfigSchema;
  tags: string[];
  author?: string;
  version?: string;
}

// UI-specific types
export interface ConfigFieldMeta {
  key: string;
  displayName: string;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'slider' | 'folder' | 'file' | 'model';
  category: ConfigCategory;
  required: boolean;
  defaultValue?: any;
  min?: number;
  max?: number;
  step?: number;
  options?: Array<{ label: string; value: any }>;
  validation?: {
    pattern?: string;
    min?: number;
    max?: number;
    required?: boolean;
  };
}

export interface ConfigDiff {
  field: string;
  oldValue: any;
  newValue: any;
  category: ConfigCategory;
}

export interface ConfigHistory {
  id: string;
  timestamp: string;
  description: string;
  changes: ConfigDiff[];
  profile_id?: string;
  user?: string;
}