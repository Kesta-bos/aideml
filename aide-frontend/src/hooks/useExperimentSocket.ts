import { useEffect, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { useExperimentStore } from '@/stores/experimentStore';
import type { WebSocketMessageType } from '@/types';

interface UseExperimentSocketOptions {
  experimentId: string;
  autoConnect?: boolean;
}

interface SocketState {
  socket: Socket | null;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastMessage: any;
  error: string | null;
}

export function useExperimentSocket({ 
  experimentId, 
  autoConnect = true 
}: UseExperimentSocketOptions) {
  const [socketState, setSocketState] = useState<SocketState>({
    socket: null,
    isConnected: false,
    connectionStatus: 'disconnected',
    lastMessage: null,
    error: null,
  });

  const {
    updateProgress,
    completeExperiment,
    failExperiment,
    setResults,
  } = useExperimentStore();

  const connect = useCallback(() => {
    if (socketState.socket?.connected) {
      return;
    }

    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const newSocket = io(`${wsUrl}/ws/experiments/${experimentId}`, {
      transports: ['websocket'],
      timeout: 10000,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    setSocketState(prev => ({ 
      ...prev, 
      socket: newSocket, 
      connectionStatus: 'connecting',
      error: null 
    }));

    // Connection events
    newSocket.on('connect', () => {
      console.log(`WebSocket connected for experiment ${experimentId}`);
      setSocketState(prev => ({ 
        ...prev, 
        isConnected: true, 
        connectionStatus: 'connected',
        error: null 
      }));
    });

    newSocket.on('disconnect', (reason) => {
      console.log(`WebSocket disconnected: ${reason}`);
      setSocketState(prev => ({ 
        ...prev, 
        isConnected: false, 
        connectionStatus: 'disconnected' 
      }));
    });

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      setSocketState(prev => ({ 
        ...prev, 
        isConnected: false, 
        connectionStatus: 'error',
        error: error.message 
      }));
    });

    // Experiment-specific events
    newSocket.on('progress', (data: any) => {
      console.log('Progress update received:', data);
      setSocketState(prev => ({ ...prev, lastMessage: data }));
      
      if (data.data) {
        updateProgress(data.data.progress || 0, data.data.currentStep || 0);
      }
    });

    newSocket.on('step_complete', (data: any) => {
      console.log('Step completed:', data);
      setSocketState(prev => ({ ...prev, lastMessage: data }));
      
      // Could trigger notifications or UI updates here
    });

    newSocket.on('experiment_complete', (data: any) => {
      console.log('Experiment completed:', data);
      setSocketState(prev => ({ ...prev, lastMessage: data }));
      
      if (data.data?.results) {
        setResults(data.data.results);
        completeExperiment(data.data.results);
      }
    });

    newSocket.on('error', (data: any) => {
      console.error('Experiment error received:', data);
      setSocketState(prev => ({ 
        ...prev, 
        lastMessage: data,
        error: data.data?.message || 'Unknown error'
      }));
      
      failExperiment(data.data?.message || 'Unknown error occurred');
    });

    // Heartbeat/ping handling
    newSocket.on('heartbeat', (data: any) => {
      // Keep connection alive
      console.log('Heartbeat received');
    });

    newSocket.on('connection_established', (data: any) => {
      console.log('Connection established:', data);
    });

    return newSocket;
  }, [experimentId, updateProgress, completeExperiment, failExperiment, setResults, socketState.socket]);

  const disconnect = useCallback(() => {
    if (socketState.socket) {
      socketState.socket.close();
      setSocketState(prev => ({ 
        ...prev, 
        socket: null, 
        isConnected: false, 
        connectionStatus: 'disconnected' 
      }));
    }
  }, [socketState.socket]);

  const sendMessage = useCallback((message: any) => {
    if (socketState.socket?.connected) {
      socketState.socket.emit('message', message);
    } else {
      console.warn('Cannot send message: socket not connected');
    }
  }, [socketState.socket]);

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect && experimentId) {
      connect();
    }

    return () => {
      if (socketState.socket) {
        socketState.socket.close();
      }
    };
  }, [experimentId, autoConnect]); // Don't include connect in deps to avoid reconnection loops

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, []);

  return {
    ...socketState,
    connect,
    disconnect,
    sendMessage,
    reconnect: connect,
  };
}
