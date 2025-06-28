import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  ExperimentConfig, 
  ExperimentResults, 
  ExperimentStatus,
  UploadedFile 
} from '@/types';

interface ExperimentState {
  // Current experiment
  currentExperiment: ExperimentConfig | null;
  isRunning: boolean;
  progress: number;
  currentStep: number;
  totalSteps: number;
  
  // Results
  results: ExperimentResults | null;
  
  // Files
  uploadedFiles: UploadedFile[];
  isUploading: boolean;
  
  // UI state
  error: string | null;
  isLoading: boolean;
  
  // Actions
  setCurrentExperiment: (experiment: ExperimentConfig | null) => void;
  updateExperimentStatus: (status: ExperimentStatus) => void;
  updateProgress: (progress: number, currentStep: number) => void;
  setResults: (results: ExperimentResults | null) => void;
  setUploadedFiles: (files: UploadedFile[]) => void;
  addUploadedFiles: (files: UploadedFile[]) => void;
  removeUploadedFile: (fileId: string) => void;
  setIsUploading: (isUploading: boolean) => void;
  setError: (error: string | null) => void;
  setIsLoading: (isLoading: boolean) => void;
  
  // Experiment lifecycle actions
  startExperiment: (totalSteps: number) => void;
  completeExperiment: (results: ExperimentResults) => void;
  failExperiment: (error: string) => void;
  stopExperiment: () => void;
  resetExperiment: () => void;
}

export const useExperimentStore = create<ExperimentState>()(
  devtools(
    (set, get) => ({
      // Initial state
      currentExperiment: null,
      isRunning: false,
      progress: 0,
      currentStep: 0,
      totalSteps: 0,
      results: null,
      uploadedFiles: [],
      isUploading: false,
      error: null,
      isLoading: false,

      // Basic setters
      setCurrentExperiment: (experiment) => 
        set({ currentExperiment: experiment }, false, 'setCurrentExperiment'),

      updateExperimentStatus: (status) =>
        set((state) => ({
          currentExperiment: state.currentExperiment 
            ? { ...state.currentExperiment, status }
            : null
        }), false, 'updateExperimentStatus'),

      updateProgress: (progress, currentStep) =>
        set({ progress, currentStep }, false, 'updateProgress'),

      setResults: (results) => 
        set({ results }, false, 'setResults'),

      setUploadedFiles: (files) => 
        set({ uploadedFiles: files }, false, 'setUploadedFiles'),

      addUploadedFiles: (files) =>
        set((state) => ({
          uploadedFiles: [...state.uploadedFiles, ...files]
        }), false, 'addUploadedFiles'),

      removeUploadedFile: (fileId) =>
        set((state) => ({
          uploadedFiles: state.uploadedFiles.filter(file => file.id !== fileId)
        }), false, 'removeUploadedFile'),

      setIsUploading: (isUploading) => 
        set({ isUploading }, false, 'setIsUploading'),

      setError: (error) => 
        set({ error }, false, 'setError'),

      setIsLoading: (isLoading) => 
        set({ isLoading }, false, 'setIsLoading'),

      // Experiment lifecycle actions
      startExperiment: (totalSteps) =>
        set({
          isRunning: true,
          progress: 0,
          currentStep: 0,
          totalSteps,
          error: null,
          results: null
        }, false, 'startExperiment'),

      completeExperiment: (results) =>
        set({
          isRunning: false,
          progress: 1,
          currentStep: get().totalSteps,
          results,
          error: null
        }, false, 'completeExperiment'),

      failExperiment: (error) =>
        set({
          isRunning: false,
          error,
          results: null
        }, false, 'failExperiment'),

      stopExperiment: () =>
        set({
          isRunning: false,
          error: null
        }, false, 'stopExperiment'),

      resetExperiment: () =>
        set({
          currentExperiment: null,
          isRunning: false,
          progress: 0,
          currentStep: 0,
          totalSteps: 0,
          results: null,
          error: null,
          isLoading: false
        }, false, 'resetExperiment'),
    }),
    {
      name: 'experiment-store',
    }
  )
);

// Selectors for common state combinations
export const useExperimentProgress = () => {
  const { progress, currentStep, totalSteps, isRunning } = useExperimentStore();
  return { progress, currentStep, totalSteps, isRunning };
};

export const useExperimentFiles = () => {
  const { uploadedFiles, isUploading, addUploadedFiles, removeUploadedFile, setIsUploading } = useExperimentStore();
  return { uploadedFiles, isUploading, addUploadedFiles, removeUploadedFile, setIsUploading };
};

export const useExperimentStatus = () => {
  const { currentExperiment, isRunning, error, isLoading } = useExperimentStore();
  return { 
    experiment: currentExperiment, 
    isRunning, 
    error, 
    isLoading,
    status: currentExperiment?.status || 'pending'
  };
};
