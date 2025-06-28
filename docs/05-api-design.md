# API Design Specification

This document provides detailed API specifications for the AIDE ML backend, including REST endpoints, WebSocket connections, and data transfer formats.

## API Overview

### Base Configuration
- **Base URL**: `http://localhost:8000` (development) / `https://api.aide.example.com` (production)
- **API Version**: v1
- **Content Type**: `application/json`
- **Authentication**: Bearer tokens (future enhancement)

### Response Format
All API responses follow a consistent format:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { /* error details */ }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## REST API Endpoints

### Experiments

#### Create Experiment
```http
POST /api/experiments
Content-Type: application/json

{
  "name": "House Price Prediction",
  "goal": "Predict house prices using the provided dataset",
  "eval": "Use RMSE metric for evaluation",
  "steps": 10,
  "files": ["file-id-1", "file-id-2"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "exp_123456789",
    "name": "House Price Prediction",
    "goal": "Predict house prices using the provided dataset",
    "eval": "Use RMSE metric for evaluation",
    "steps": 10,
    "status": "pending",
    "createdAt": "2024-01-15T10:30:00Z",
    "dataDir": "/experiments/exp_123456789/data"
  }
}
```

#### Get Experiment
```http
GET /api/experiments/{experiment_id}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "exp_123456789",
    "name": "House Price Prediction",
    "status": "running",
    "progress": 0.3,
    "currentStep": 3,
    "totalSteps": 10,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:35:00Z"
  }
}
```

#### Start Experiment
```http
POST /api/experiments/{experiment_id}/start
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "exp_123456789",
    "status": "running",
    "startedAt": "2024-01-15T10:35:00Z"
  }
}
```

#### Stop Experiment
```http
POST /api/experiments/{experiment_id}/stop
```

#### Get Experiment Results
```http
GET /api/experiments/{experiment_id}/results
```

**Response**:
```json
{
  "success": true,
  "data": {
    "experimentId": "exp_123456789",
    "status": "completed",
    "bestSolution": {
      "code": "# Python code here...",
      "metric": {
        "value": 0.85,
        "maximize": true
      }
    },
    "journal": {
      "nodes": [
        {
          "id": "node_1",
          "step": 1,
          "code": "# Step 1 code...",
          "metric": { "value": 0.75, "maximize": true },
          "isBuggy": false,
          "execTime": 2.5
        }
      ]
    },
    "treeVisualization": "/api/experiments/exp_123456789/tree.html",
    "completedAt": "2024-01-15T10:45:00Z"
  }
}
```

#### List Experiments
```http
GET /api/experiments?page=1&limit=10&status=completed
```

### File Management

#### Upload Files
```http
POST /api/upload
Content-Type: multipart/form-data

files: [File, File, ...]
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "file_123",
      "filename": "train.csv",
      "originalName": "housing_data.csv",
      "size": 1048576,
      "mimeType": "text/csv",
      "uploadedAt": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### Get File Info
```http
GET /api/files/{file_id}
```

#### Download File
```http
GET /api/files/{file_id}/download
```

#### Delete File
```http
DELETE /api/files/{file_id}
```

### Configuration

#### Get Application Config
```http
GET /api/config
```

**Response**:
```json
{
  "success": true,
  "data": {
    "maxFileSize": 104857600,
    "allowedFileTypes": ["csv", "json", "txt", "zip"],
    "maxExperimentSteps": 50,
    "supportedModels": ["gpt-4", "claude-3", "gpt-3.5-turbo"]
  }
}
```

#### Validate API Key
```http
POST /api/config/validate-api-key
Content-Type: application/json

{
  "provider": "openai",
  "apiKey": "sk-..."
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "valid": true,
    "provider": "openai",
    "model": "gpt-4"
  }
}
```

## WebSocket API

### Connection
```javascript
const socket = io('ws://localhost:8000/ws/experiments/exp_123456789');
```

### Message Types

#### Progress Updates
```json
{
  "type": "progress",
  "data": {
    "experimentId": "exp_123456789",
    "currentStep": 3,
    "totalSteps": 10,
    "progress": 0.3,
    "status": "running"
  }
}
```

#### Step Completion
```json
{
  "type": "step_complete",
  "data": {
    "experimentId": "exp_123456789",
    "step": 3,
    "node": {
      "id": "node_3",
      "code": "# Generated code...",
      "metric": { "value": 0.82, "maximize": true },
      "execTime": 3.2,
      "isBuggy": false
    }
  }
}
```

#### Experiment Complete
```json
{
  "type": "experiment_complete",
  "data": {
    "experimentId": "exp_123456789",
    "status": "completed",
    "bestMetric": { "value": 0.89, "maximize": true },
    "totalTime": 125.5,
    "completedAt": "2024-01-15T10:45:00Z"
  }
}
```

#### Error Notifications
```json
{
  "type": "error",
  "data": {
    "experimentId": "exp_123456789",
    "error": "EXECUTION_ERROR",
    "message": "Code execution failed",
    "step": 5,
    "details": {
      "exception": "ValueError: Invalid input shape",
      "traceback": "..."
    }
  }
}
```

#### Configuration Updates
```json
{
  "type": "config_update",
  "data": {
    "experimentId": "exp_123456789",
    "config": {
      "model": "gpt-4",
      "temperature": 0.5,
      "maxTokens": 4000
    }
  }
}
```

## Error Codes

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

### Application Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `EXPERIMENT_NOT_FOUND` - Experiment does not exist
- `EXPERIMENT_ALREADY_RUNNING` - Cannot start running experiment
- `FILE_NOT_FOUND` - Uploaded file not found
- `FILE_TOO_LARGE` - File exceeds size limit
- `INVALID_FILE_TYPE` - Unsupported file format
- `API_KEY_INVALID` - External API key validation failed
- `EXECUTION_ERROR` - Code execution failed
- `TIMEOUT_ERROR` - Operation timed out

## Rate Limiting

### Limits
- **General API**: 100 requests per minute per IP
- **File Upload**: 10 uploads per minute per IP
- **Experiment Creation**: 5 experiments per hour per IP
- **WebSocket Connections**: 5 concurrent connections per IP

### Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248000
```

## Authentication (Future Enhancement)

### JWT Token Format
```json
{
  "sub": "user_123",
  "email": "user@example.com",
  "role": "user",
  "exp": 1642248000,
  "iat": 1642244400
}
```

### Protected Endpoints
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Client Examples

### JavaScript/TypeScript
```typescript
// api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

export const experimentAPI = {
  create: (config: ExperimentConfig) =>
    apiClient.post('/api/experiments', config),
  
  start: (id: string) =>
    apiClient.post(`/api/experiments/${id}/start`),
  
  getResults: (id: string) =>
    apiClient.get(`/api/experiments/${id}/results`),
};

export const fileAPI = {
  upload: (files: FileList) => {
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    return apiClient.post('/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};
```

### Python Client
```python
# client.py
import requests
import json
from typing import Dict, Any

class AIDEClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def create_experiment(self, config: Dict[str, Any]) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/experiments",
            json=config
        )
        response.raise_for_status()
        return response.json()
    
    def start_experiment(self, experiment_id: str) -> Dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/api/experiments/{experiment_id}/start"
        )
        response.raise_for_status()
        return response.json()
```
