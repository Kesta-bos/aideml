# Technical Specifications

This document provides detailed technical specifications for the React-based AIDE ML application, including data models, API specifications, authentication, configuration, and deployment requirements.

## Data Models and Schemas

### Core Data Models

#### Experiment Configuration
```typescript
interface ExperimentConfig {
  id: string;
  name: string;
  dataDir: string;
  goal: string;
  eval?: string;
  steps: number;
  createdAt: Date;
  updatedAt: Date;
  status: 'pending' | 'running' | 'completed' | 'failed';
}
```

#### Node (Solution Step)
```typescript
interface Node {
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
  
  // Timestamps
  createdAt: Date;
}
```

#### Metric Value
```typescript
interface MetricValue {
  value: number | null;
  maximize?: boolean;
}

interface WorstMetricValue extends MetricValue {
  value: null;
}
```

#### Journal (Experiment History)
```typescript
interface Journal {
  experimentId: string;
  nodes: Node[];
  draftNodes: Node[];
  buggyNodes: Node[];
  createdAt: Date;
  updatedAt: Date;
}
```

#### File Upload
```typescript
interface UploadedFile {
  id: string;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  path: string;
  uploadedAt: Date;
}
```

### Backend Data Models (Pydantic)

```python
# models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ExperimentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ExperimentConfig(BaseModel):
    id: str = Field(..., description="Unique experiment identifier")
    name: str = Field(..., description="Human-readable experiment name")
    data_dir: str = Field(..., description="Path to experiment data")
    goal: str = Field(..., description="Experiment objective")
    eval: Optional[str] = Field(None, description="Evaluation criteria")
    steps: int = Field(10, ge=1, le=50, description="Number of steps to run")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: ExperimentStatus = Field(ExperimentStatus.PENDING)

class MetricValue(BaseModel):
    value: Optional[float] = None
    maximize: Optional[bool] = None

class Node(BaseModel):
    id: str
    step: int
    code: str
    plan: Optional[str] = None
    parent_id: Optional[str] = None
    children: List[str] = Field(default_factory=list)
    
    # Execution info
    term_out: List[str] = Field(default_factory=list)
    exec_time: Optional[float] = None
    exc_type: Optional[str] = None
    exc_info: Optional[Dict[str, Any]] = None
    exc_stack: Optional[List[tuple]] = None
    
    # Evaluation
    analysis: Optional[str] = None
    metric: Optional[MetricValue] = None
    is_buggy: bool = False
    debug_depth: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## API Specifications

### REST API Endpoints

#### Experiments
```python
# FastAPI route definitions

@app.post("/api/experiments", response_model=ExperimentConfig)
async def create_experiment(config: ExperimentConfig):
    """Create a new experiment"""
    pass

@app.get("/api/experiments/{experiment_id}", response_model=ExperimentConfig)
async def get_experiment(experiment_id: str):
    """Get experiment details"""
    pass

@app.post("/api/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start experiment execution"""
    pass

@app.get("/api/experiments/{experiment_id}/status")
async def get_experiment_status(experiment_id: str):
    """Get current experiment status"""
    pass

@app.get("/api/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str):
    """Get experiment results and journal"""
    pass

@app.delete("/api/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str):
    """Delete an experiment"""
    pass
```

#### File Management
```python
@app.post("/api/upload", response_model=List[UploadedFile])
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload experiment data files"""
    pass

@app.get("/api/files/{file_id}")
async def download_file(file_id: str):
    """Download a specific file"""
    pass

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file"""
    pass
```

#### Configuration
```python
@app.get("/api/config")
async def get_config():
    """Get application configuration"""
    pass

@app.post("/api/config/validate-api-key")
async def validate_api_key(provider: str, api_key: str):
    """Validate API key for external services"""
    pass
```

### WebSocket API

#### Real-time Updates
```python
@app.websocket("/ws/experiments/{experiment_id}")
async def experiment_websocket(websocket: WebSocket, experiment_id: str):
    """WebSocket endpoint for real-time experiment updates"""
    await websocket.accept()
    
    # Send updates during experiment execution
    # - Progress updates
    # - Step completion
    # - Error notifications
    # - Result updates
```

#### WebSocket Message Types
```typescript
// Frontend WebSocket message types
interface ProgressUpdate {
  type: 'progress';
  experimentId: string;
  currentStep: number;
  totalSteps: number;
  progress: number; // 0-1
}

interface StepComplete {
  type: 'step_complete';
  experimentId: string;
  step: number;
  node: Node;
}

interface ExperimentComplete {
  type: 'experiment_complete';
  experimentId: string;
  results: ExperimentResults;
}

interface ErrorNotification {
  type: 'error';
  experimentId: string;
  error: string;
  details?: any;
}
```

## Authentication and Authorization

### Current State
- No authentication in Streamlit version
- API keys stored in session state
- Single-user application

### Proposed Authentication (Future Enhancement)

#### JWT-based Authentication
```typescript
interface AuthUser {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
  createdAt: Date;
}

interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresAt: Date;
}
```

#### API Key Management
```typescript
interface ApiKeyConfig {
  openaiKey?: string;
  anthropicKey?: string;
  openrouterKey?: string;
  encrypted: boolean;
  userId: string;
}
```

## Configuration Management

### Environment Variables

#### Backend (.env)
```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Database (future)
DATABASE_URL=postgresql://user:pass@localhost/aide

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=csv,json,txt,zip,xlsx

# External APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=24h

# CORS
CORS_ORIGINS=http://localhost:3000,https://aide.example.com
```

#### Frontend (.env)
```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Application
VITE_APP_NAME=AIDE ML
VITE_APP_VERSION=2.0.0

# Features
VITE_ENABLE_AUTH=false
VITE_MAX_UPLOAD_SIZE=104857600
VITE_SUPPORTED_FORMATS=csv,json,txt,zip,xlsx
```

### Configuration Schema
```typescript
// config/app.config.ts
interface AppConfig {
  api: {
    baseUrl: string;
    wsUrl: string;
    timeout: number;
  };
  upload: {
    maxSize: number;
    allowedTypes: string[];
    chunkSize: number;
  };
  experiment: {
    maxSteps: number;
    defaultSteps: number;
    timeoutMinutes: number;
  };
  ui: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    autoSave: boolean;
  };
}
```

## Build and Deployment

### Development Setup

#### Backend Development
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Production Deployment

#### Docker Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./aide-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/aide
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - db

  frontend:
    build: ./aide-frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=aide
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### Kubernetes Deployment (Optional)
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aide-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aide-backend
  template:
    metadata:
      labels:
        app: aide-backend
    spec:
      containers:
      - name: backend
        image: aide/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: aide-secrets
              key: database-url
```

### CI/CD Pipeline

#### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy AIDE ML

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Test Backend
        run: |
          cd aide-backend
          pip install -r requirements.txt
          pytest
      - name: Test Frontend
        run: |
          cd aide-frontend
          npm ci
          npm run test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deployment commands
```

## Performance Considerations

### Backend Optimization
- Async/await for I/O operations
- Connection pooling for database
- Caching for frequently accessed data
- Background tasks for long-running experiments

### Frontend Optimization
- Code splitting and lazy loading
- Bundle size optimization
- Image optimization
- Service worker for caching

### Monitoring and Logging
- Application performance monitoring (APM)
- Error tracking (Sentry)
- Structured logging
- Health check endpoints

## Security Considerations

### Data Protection
- Input validation and sanitization
- File upload security
- SQL injection prevention
- XSS protection

### API Security
- Rate limiting
- CORS configuration
- Request size limits
- API key encryption

### Infrastructure Security
- HTTPS enforcement
- Security headers
- Container security scanning
- Regular dependency updates

## Testing Strategy

### Backend Testing
```python
# tests/test_experiments.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_experiment():
    experiment_data = {
        "name": "Test Experiment",
        "goal": "Predict house prices",
        "steps": 5
    }
    response = client.post("/api/experiments", json=experiment_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Experiment"

def test_start_experiment():
    # Create experiment first
    experiment = create_test_experiment()

    response = client.post(f"/api/experiments/{experiment['id']}/start")
    assert response.status_code == 200
```

### Frontend Testing
```typescript
// __tests__/components/ExperimentForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ExperimentForm } from '../components/ExperimentForm';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } }
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

test('creates experiment with valid data', async () => {
  const mockOnSubmit = jest.fn();

  renderWithProviders(<ExperimentForm onSubmit={mockOnSubmit} />);

  fireEvent.change(screen.getByLabelText(/goal/i), {
    target: { value: 'Predict house prices' }
  });

  fireEvent.click(screen.getByRole('button', { name: /run aide/i }));

  await waitFor(() => {
    expect(mockOnSubmit).toHaveBeenCalledWith({
      goal: 'Predict house prices',
      steps: 10
    });
  });
});
```
