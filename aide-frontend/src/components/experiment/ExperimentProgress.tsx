import React, { useEffect, useState } from 'react';
import { Card, Progress, Typography, Spin, Button, Space } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, StopOutlined } from '@ant-design/icons';
import { io, Socket } from 'socket.io-client';
import { useMutation } from '@tanstack/react-query';
import { experimentAPI } from '@/services/api';
import { useExperimentStore } from '@/stores/experimentStore';
import type { ExperimentConfig, WebSocketMessageType } from '@/types';

const { Title, Text } = Typography;

interface ExperimentProgressProps {
  experiment: ExperimentConfig;
}

export function ExperimentProgress({ experiment }: ExperimentProgressProps) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  const {
    progress,
    currentStep,
    totalSteps,
    isRunning,
    updateProgress,
    completeExperiment,
    failExperiment,
    stopExperiment,
    setResults
  } = useExperimentStore();

  const stopMutation = useMutation({
    mutationFn: () => experimentAPI.stop(experiment.id),
    onSuccess: () => {
      stopExperiment();
    },
  });

  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const newSocket = io(`${wsUrl}/ws/experiments/${experiment.id}`);

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      setConnectionStatus('connected');
    });

    newSocket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      setConnectionStatus('disconnected');
    });

    newSocket.on('progress', (data: any) => {
      console.log('Progress update:', data);
      updateProgress(data.data.progress, data.data.currentStep);
    });

    newSocket.on('step_complete', (data: any) => {
      console.log('Step completed:', data);
      // Could show step completion notifications here
    });

    newSocket.on('experiment_complete', (data: any) => {
      console.log('Experiment completed:', data);
      if (data.data.results) {
        setResults(data.data.results);
        completeExperiment(data.data.results);
      }
    });

    newSocket.on('error', (data: any) => {
      console.error('Experiment error:', data);
      failExperiment(data.data.message || 'Unknown error occurred');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [experiment.id, updateProgress, completeExperiment, failExperiment, setResults]);

  const getStatusText = () => {
    if (connectionStatus === 'connecting') {
      return 'Connecting to experiment...';
    }
    if (connectionStatus === 'disconnected') {
      return 'Connection lost. Attempting to reconnect...';
    }
    if (!isRunning) {
      return 'Experiment stopped';
    }
    return `Running Step ${currentStep}/${totalSteps || experiment.steps}`;
  };

  const getProgressPercent = () => {
    if (totalSteps > 0) {
      return Math.round((currentStep / totalSteps) * 100);
    }
    return Math.round(progress * 100);
  };

  return (
    <Card className="slide-up">
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={3} style={{ margin: 0, marginBottom: 8 }}>
          🔥 {experiment.name}
        </Title>
        <Text type="secondary">{getStatusText()}</Text>
      </div>

      <div style={{ marginBottom: 24 }}>
        <Progress
          percent={getProgressPercent()}
          status={
            connectionStatus === 'disconnected' ? 'exception' :
            !isRunning ? 'normal' : 'active'
          }
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          format={(percent) => `${percent}%`}
        />

        {isRunning && (
          <div style={{ textAlign: 'center', marginTop: 12 }}>
            <Text style={{ fontSize: 14 }}>
              Step {currentStep} of {totalSteps || experiment.steps}
            </Text>
          </div>
        )}
      </div>

      {connectionStatus === 'connecting' && (
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <Spin size="small" />
          <Text style={{ marginLeft: 8, color: '#666' }}>
            Establishing connection...
          </Text>
        </div>
      )}

      {connectionStatus === 'disconnected' && (
        <div style={{
          textAlign: 'center',
          marginBottom: 16,
          padding: 12,
          background: '#fff2f0',
          borderRadius: 6,
          border: '1px solid #ffccc7'
        }}>
          <Text style={{ color: '#cf1322' }}>
            ⚠️ Connection lost. Real-time updates unavailable.
          </Text>
        </div>
      )}

      {isRunning && (
        <div style={{ textAlign: 'center' }}>
          <Space>
            <Button
              type="default"
              icon={<StopOutlined />}
              onClick={() => stopMutation.mutate()}
              loading={stopMutation.isPending}
              danger
            >
              Stop Experiment
            </Button>
          </Space>
        </div>
      )}

      {experiment.goal && (
        <div style={{
          marginTop: 24,
          padding: 16,
          background: '#f6f8fa',
          borderRadius: 8
        }}>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            Goal:
          </Text>
          <Text style={{ fontSize: 13 }}>
            {experiment.goal}
          </Text>

          {experiment.eval && (
            <>
              <Text strong style={{ display: 'block', marginTop: 12, marginBottom: 8 }}>
                Evaluation:
              </Text>
              <Text style={{ fontSize: 13 }}>
                {experiment.eval}
              </Text>
            </>
          )}
        </div>
      )}
    </Card>
  );
}
