// Type definitions for AIDE ML Frontend

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
  timestamp: string;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: string;
}

export type ExperimentStatus = 'pending' | 'running' | 'completed' | 'failed' | 'stopped';

export interface MetricValue {
  value: number | null;
  maximize?: boolean;
}

export interface Node {
  id: string;
  step: number;
  code: string;
  plan?: string;
  parentId?: string;
  children: string[];
  
  // Execution info
  termOut: string[];
  execTime?: number;
  excType?: string;
  excInfo?: Record<string, any>;
  excStack?: Array<[string, number, string, string]>;
  
  // Evaluation
  analysis?: string;
  metric?: MetricValue;
  isBuggy: boolean;
  debugDepth: number;
  
  createdAt: string;
}

export interface Journal {
  experimentId: string;
  nodes: Node[];
  draftNodes: Node[];
  buggyNodes: Node[];
  createdAt: string;
  updatedAt: string;
}

export interface ExperimentConfig {
  id: string;
  name: string;
  dataDir: string;
  goal: string;
  eval?: string;
  steps: number;
  
  // Status and progress
  status: ExperimentStatus;
  progress: number;
  currentStep: number;
  
  // File associations
  files: string[];
  
  // Timestamps
  createdAt: string;
  updatedAt: string;
  startedAt?: string;
  completedAt?: string;
}

export interface ExperimentCreateRequest {
  name: string;
  goal: string;
  eval?: string;
  steps: number;
  files: string[];
}

export interface ExperimentResults {
  experimentId: string;
  status: ExperimentStatus;
  
  bestSolution?: {
    code: string;
    metric: MetricValue;
  };
  journal: Journal;
  treeVisualization?: string;
  config: Record<string, any>;
  
  // Performance metrics
  totalTime?: number;
  bestMetric?: MetricValue;
  
  completedAt?: string;
}

export interface UploadedFile {
  id: string;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  uploadedAt: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  experimentId: string;
}

export interface ProgressUpdate extends WebSocketMessage {
  type: 'progress';
  data: {
    experimentId: string;
    currentStep: number;
    totalSteps: number;
    progress: number;
    status: string;
  };
}

export interface StepComplete extends WebSocketMessage {
  type: 'step_complete';
  data: {
    experimentId: string;
    step: number;
    node: Partial<Node>;
  };
}

export interface ExperimentComplete extends WebSocketMessage {
  type: 'experiment_complete';
  data: {
    experimentId: string;
    status: string;
    results: ExperimentResults;
  };
}

export interface ErrorNotification extends WebSocketMessage {
  type: 'error';
  data: {
    experimentId: string;
    error: string;
    message: string;
    details?: any;
  };
}

export type WebSocketMessageType = 
  | ProgressUpdate 
  | StepComplete 
  | ExperimentComplete 
  | ErrorNotification;

// Configuration types
export interface AppConfig {
  api: {
    baseUrl: string;
    wsUrl: string;
    timeout: number;
  };
  upload: {
    maxSize: number;
    allowedTypes: string[];
  };
  experiment: {
    maxSteps: number;
    defaultSteps: number;
  };
}

// API key configuration
export interface ApiKeyConfig {
  openaiKey?: string;
  anthropicKey?: string;
  openrouterKey?: string;
}

// Form types
export interface ExperimentFormData {
  name: string;
  goal: string;
  eval?: string;
  steps: number;
  files: File[];
}

// UI state types
export interface ExperimentState {
  currentExperiment: ExperimentConfig | null;
  isRunning: boolean;
  progress: number;
  currentStep: number;
  results: ExperimentResults | null;
  error: string | null;
}

export interface FileUploadState {
  uploadedFiles: UploadedFile[];
  isUploading: boolean;
  uploadProgress: number;
  error: string | null;
}
