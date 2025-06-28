# Implementation Examples

This document provides practical code examples for implementing the React frontend and FastAPI backend for AIDE ML.

## React Frontend Examples

### Main App Component
```tsx
// src/App.tsx
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ExperimentPage } from './pages/ExperimentPage';
import { ResultsPage } from './pages/ResultsPage';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const theme = {
  token: {
    colorPrimary: '#0D0F18',
    colorBgBase: '#F0EFE9',
  },
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={theme}>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<ExperimentPage />} />
              <Route path="/results/:experimentId" element={<ResultsPage />} />
            </Routes>
          </Layout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
```

### Experiment Form Component
```tsx
// src/components/ExperimentForm.tsx
import React, { useState } from 'react';
import { Form, Input, Slider, Button, Upload, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { experimentAPI, fileAPI } from '../services/api';
import type { ExperimentConfig } from '../types';

const { TextArea } = Input;

interface ExperimentFormProps {
  onExperimentCreated: (experiment: ExperimentConfig) => void;
}

export function ExperimentForm({ onExperimentCreated }: ExperimentFormProps) {
  const [form] = Form.useForm();
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  const uploadMutation = useMutation({
    mutationFn: fileAPI.upload,
    onSuccess: (data) => {
      const fileIds = data.data.map((file: any) => file.id);
      setUploadedFiles(prev => [...prev, ...fileIds]);
      message.success(`${data.data.length} files uploaded successfully`);
    },
    onError: () => {
      message.error('File upload failed');
    },
  });

  const createExperimentMutation = useMutation({
    mutationFn: experimentAPI.create,
    onSuccess: (data) => {
      onExperimentCreated(data.data);
      form.resetFields();
      setUploadedFiles([]);
    },
    onError: () => {
      message.error('Failed to create experiment');
    },
  });

  const handleSubmit = (values: any) => {
    createExperimentMutation.mutate({
      ...values,
      files: uploadedFiles,
    });
  };

  const uploadProps = {
    multiple: true,
    accept: '.csv,.json,.txt,.zip',
    beforeUpload: (file: File) => {
      const isValidSize = file.size <= 100 * 1024 * 1024; // 100MB
      if (!isValidSize) {
        message.error('File must be smaller than 100MB');
        return false;
      }
      return false; // Prevent auto upload
    },
    onChange: (info: any) => {
      if (info.fileList.length > 0) {
        uploadMutation.mutate(info.fileList.map((f: any) => f.originFileObj));
      }
    },
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{ steps: 10 }}
    >
      <Form.Item
        name="name"
        label="Experiment Name"
        rules={[{ required: true, message: 'Please enter experiment name' }]}
      >
        <Input placeholder="e.g., House Price Prediction" />
      </Form.Item>

      <Form.Item
        name="goal"
        label="Goal"
        rules={[{ required: true, message: 'Please enter experiment goal' }]}
      >
        <TextArea
          rows={3}
          placeholder="Example: Predict the sales price for each house"
        />
      </Form.Item>

      <Form.Item
        name="eval"
        label="Evaluation Criteria"
      >
        <TextArea
          rows={2}
          placeholder="Example: Use the RMSE metric between the logarithm of the predicted and observed values"
        />
      </Form.Item>

      <Form.Item
        name="steps"
        label="Number of Steps"
      >
        <Slider
          min={1}
          max={20}
          marks={{ 1: '1', 10: '10', 20: '20' }}
        />
      </Form.Item>

      <Form.Item label="Upload Dataset">
        <Upload {...uploadProps}>
          <Button icon={<UploadOutlined />} loading={uploadMutation.isPending}>
            Upload Files
          </Button>
        </Upload>
        {uploadedFiles.length > 0 && (
          <div style={{ marginTop: 8, color: '#52c41a' }}>
            {uploadedFiles.length} file(s) uploaded
          </div>
        )}
      </Form.Item>

      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          size="large"
          block
          loading={createExperimentMutation.isPending}
          disabled={uploadedFiles.length === 0}
        >
          Run AIDE
        </Button>
      </Form.Item>
    </Form>
  );
}
```

### Real-time Progress Component
```tsx
// src/components/ExperimentProgress.tsx
import React, { useEffect, useState } from 'react';
import { Progress, Card, Typography, Spin } from 'antd';
import { io, Socket } from 'socket.io-client';
import type { ExperimentConfig } from '../types';

const { Title, Text } = Typography;

interface ExperimentProgressProps {
  experiment: ExperimentConfig;
  onComplete: (results: any) => void;
}

export function ExperimentProgress({ experiment, onComplete }: ExperimentProgressProps) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [status, setStatus] = useState<string>('connecting');

  useEffect(() => {
    const newSocket = io(`${process.env.VITE_WS_URL}/ws/experiments/${experiment.id}`);

    newSocket.on('connect', () => {
      setStatus('connected');
    });

    newSocket.on('progress', (data) => {
      setProgress(data.progress * 100);
      setCurrentStep(data.currentStep);
      setStatus('running');
    });

    newSocket.on('step_complete', (data) => {
      console.log('Step completed:', data.step);
    });

    newSocket.on('experiment_complete', (data) => {
      setStatus('completed');
      setProgress(100);
      onComplete(data);
    });

    newSocket.on('error', (data) => {
      console.error('Experiment error:', data);
      setStatus('error');
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [experiment.id, onComplete]);

  const getStatusText = () => {
    switch (status) {
      case 'connecting':
        return 'Connecting to experiment...';
      case 'connected':
        return 'Connected, waiting for experiment to start...';
      case 'running':
        return `Running Step ${currentStep}/${experiment.steps}`;
      case 'completed':
        return 'Experiment completed successfully!';
      case 'error':
        return 'An error occurred during the experiment';
      default:
        return 'Unknown status';
    }
  };

  return (
    <Card>
      <div style={{ textAlign: 'center', marginBottom: 24 }}>
        <Title level={3}>🔥 {experiment.name}</Title>
        <Text type="secondary">{getStatusText()}</Text>
      </div>

      <Progress
        percent={progress}
        status={status === 'error' ? 'exception' : 'active'}
        strokeColor={{
          '0%': '#108ee9',
          '100%': '#87d068',
        }}
      />

      {status === 'connecting' && (
        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <Spin size="small" />
          <Text style={{ marginLeft: 8 }}>Establishing connection...</Text>
        </div>
      )}
    </Card>
  );
}
```

### Results Display Component
```tsx
// src/components/ResultsDisplay.tsx
import React from 'react';
import { Tabs, Card, Statistic, Typography } from 'antd';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { TreeVisualization } from './TreeVisualization';
import type { ExperimentResults } from '../types';

const { Text } = Typography;

interface ResultsDisplayProps {
  results: ExperimentResults;
}

export function ResultsDisplay({ results }: ResultsDisplayProps) {
  const items = [
    {
      key: 'tree',
      label: 'Tree Visualization',
      children: <TreeVisualization htmlContent={results.treeVisualization} />,
    },
    {
      key: 'solution',
      label: 'Best Solution',
      children: (
        <Card>
          <Statistic
            title="Best Validation Score"
            value={results.bestSolution.metric.value}
            precision={4}
            valueStyle={{ color: '#3f8600' }}
          />
          <div style={{ marginTop: 16 }}>
            <Text strong>Generated Code:</Text>
            <SyntaxHighlighter
              language="python"
              style={docco}
              customStyle={{
                maxHeight: '400px',
                overflow: 'auto',
                marginTop: 8,
              }}
            >
              {results.bestSolution.code}
            </SyntaxHighlighter>
          </div>
        </Card>
      ),
    },
    {
      key: 'journal',
      label: 'Journal',
      children: (
        <div>
          {results.journal.nodes.map((node, index) => (
            <Card key={node.id} style={{ marginBottom: 16 }}>
              <Text strong>Step {node.step}</Text>
              <div style={{ marginTop: 8 }}>
                <Text type="secondary">
                  Metric: {node.metric?.value?.toFixed(4) || 'N/A'} | 
                  Execution Time: {node.execTime?.toFixed(2)}s |
                  Status: {node.isBuggy ? 'Buggy' : 'Success'}
                </Text>
              </div>
              {node.analysis && (
                <div style={{ marginTop: 8 }}>
                  <Text>{node.analysis}</Text>
                </div>
              )}
            </Card>
          ))}
        </div>
      ),
    },
  ];

  return <Tabs items={items} />;
}
```

## FastAPI Backend Examples

### Main Application Setup
```python
# main.py
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from typing import List
import os

from models import ExperimentConfig, ExperimentResponse
from services import ExperimentService, FileService
from websocket_manager import WebSocketManager

app = FastAPI(
    title="AIDE ML API",
    description="API for AIDE Machine Learning Agent",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for serving visualizations
app.mount("/static", StaticFiles(directory="static"), name="static")

# Services
experiment_service = ExperimentService()
file_service = FileService()
websocket_manager = WebSocketManager()

@app.get("/")
async def root():
    return {"message": "AIDE ML API", "version": "2.0.0"}

@app.post("/api/experiments", response_model=ExperimentResponse)
async def create_experiment(config: ExperimentConfig):
    try:
        experiment = await experiment_service.create(config)
        return ExperimentResponse(success=True, data=experiment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    try:
        await experiment_service.start(experiment_id, websocket_manager)
        return {"success": True, "message": "Experiment started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str):
    try:
        results = await experiment_service.get_results(experiment_id)
        return {"success": True, "data": results}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        uploaded_files = await file_service.upload_multiple(files)
        return {"success": True, "data": uploaded_files}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws/experiments/{experiment_id}")
async def websocket_endpoint(websocket: WebSocket, experiment_id: str):
    await websocket_manager.connect(websocket, experiment_id)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

### Experiment Service
```python
# services/experiment_service.py
import asyncio
import uuid
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from models import ExperimentConfig, Experiment
from aide import Experiment as AIDEExperiment
from websocket_manager import WebSocketManager

class ExperimentService:
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.running_experiments: Dict[str, asyncio.Task] = {}

    async def create(self, config: ExperimentConfig) -> Experiment:
        experiment_id = f"exp_{uuid.uuid4().hex[:12]}"
        
        experiment = Experiment(
            id=experiment_id,
            name=config.name,
            goal=config.goal,
            eval=config.eval,
            steps=config.steps,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        self.experiments[experiment_id] = experiment
        return experiment

    async def start(self, experiment_id: str, websocket_manager: WebSocketManager):
        if experiment_id not in self.experiments:
            raise ValueError("Experiment not found")
        
        experiment = self.experiments[experiment_id]
        if experiment.status == "running":
            raise ValueError("Experiment is already running")
        
        experiment.status = "running"
        experiment.started_at = datetime.utcnow()
        
        # Start experiment in background
        task = asyncio.create_task(
            self._run_experiment(experiment, websocket_manager)
        )
        self.running_experiments[experiment_id] = task

    async def _run_experiment(self, experiment: Experiment, websocket_manager: WebSocketManager):
        try:
            # Initialize AIDE experiment
            aide_experiment = AIDEExperiment(
                data_dir=f"./uploads/{experiment.id}",
                goal=experiment.goal,
                eval=experiment.eval
            )
            
            # Run experiment with progress updates
            for step in range(experiment.steps):
                # Send progress update
                await websocket_manager.send_to_experiment(
                    experiment.id,
                    {
                        "type": "progress",
                        "data": {
                            "experimentId": experiment.id,
                            "currentStep": step + 1,
                            "totalSteps": experiment.steps,
                            "progress": (step + 1) / experiment.steps,
                            "status": "running"
                        }
                    }
                )
                
                # Run one step
                aide_experiment.run(steps=1)
                
                # Send step completion
                await websocket_manager.send_to_experiment(
                    experiment.id,
                    {
                        "type": "step_complete",
                        "data": {
                            "experimentId": experiment.id,
                            "step": step + 1
                        }
                    }
                )
            
            # Experiment completed
            experiment.status = "completed"
            experiment.completed_at = datetime.utcnow()
            
            # Get final results
            best_node = aide_experiment.journal.get_best_node(only_good=False)
            results = {
                "bestSolution": {
                    "code": best_node.code,
                    "metric": {
                        "value": best_node.metric.value,
                        "maximize": best_node.metric.maximize
                    }
                },
                "journal": {
                    "nodes": [
                        {
                            "id": node.id,
                            "step": node.step,
                            "code": node.code,
                            "metric": {
                                "value": node.metric.value if node.metric else None,
                                "maximize": node.metric.maximize if node.metric else None
                            },
                            "isBuggy": node.is_buggy,
                            "execTime": node.exec_time
                        }
                        for node in aide_experiment.journal.nodes
                    ]
                }
            }
            
            # Send completion notification
            await websocket_manager.send_to_experiment(
                experiment.id,
                {
                    "type": "experiment_complete",
                    "data": {
                        "experimentId": experiment.id,
                        "status": "completed",
                        "results": results
                    }
                }
            )
            
        except Exception as e:
            experiment.status = "failed"
            await websocket_manager.send_to_experiment(
                experiment.id,
                {
                    "type": "error",
                    "data": {
                        "experimentId": experiment.id,
                        "error": "EXECUTION_ERROR",
                        "message": str(e)
                    }
                }
            )
        finally:
            # Clean up
            if experiment.id in self.running_experiments:
                del self.running_experiments[experiment.id]

    async def get_results(self, experiment_id: str) -> Dict[str, Any]:
        if experiment_id not in self.experiments:
            raise ValueError("Experiment not found")
        
        experiment = self.experiments[experiment_id]
        if experiment.status != "completed":
            raise ValueError("Experiment not completed yet")
        
        # Return stored results
        return experiment.results
```

### WebSocket Manager
```python
# websocket_manager.py
from fastapi import WebSocket
from typing import Dict, List
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, experiment_id: str):
        await websocket.accept()
        
        if experiment_id not in self.active_connections:
            self.active_connections[experiment_id] = []
        
        self.active_connections[experiment_id].append(websocket)
        
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except:
            # Connection closed
            self.disconnect(websocket, experiment_id)

    def disconnect(self, websocket: WebSocket, experiment_id: str):
        if experiment_id in self.active_connections:
            self.active_connections[experiment_id].remove(websocket)
            if not self.active_connections[experiment_id]:
                del self.active_connections[experiment_id]

    async def send_to_experiment(self, experiment_id: str, message: dict):
        if experiment_id in self.active_connections:
            for connection in self.active_connections[experiment_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    # Remove dead connections
                    self.active_connections[experiment_id].remove(connection)
```

This completes the comprehensive migration documentation with practical implementation examples for both frontend and backend components.
