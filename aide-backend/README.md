# AIDE ML Backend API

FastAPI backend for the AIDE Machine Learning Engineer Agent React frontend.

## Features

- **REST API**: Complete experiment management endpoints
- **WebSocket Support**: Real-time experiment progress updates
- **File Management**: Upload and manage experiment datasets
- **AIDE Integration**: Direct integration with existing AIDE ML engine
- **CORS Enabled**: Ready for React frontend integration

## Quick Start

### Development Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Development Server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

### Docker Setup

1. **Build Image**:
   ```bash
   docker build -t aide-backend .
   ```

2. **Run Container**:
   ```bash
   docker run -p 8000:8000 --env-file .env aide-backend
   ```

## API Endpoints

### Experiments
- `POST /api/experiments` - Create new experiment
- `GET /api/experiments/{id}` - Get experiment details
- `POST /api/experiments/{id}/start` - Start experiment
- `GET /api/experiments/{id}/results` - Get results
- `DELETE /api/experiments/{id}` - Delete experiment

### File Management
- `POST /api/upload` - Upload files
- `GET /api/files/{id}` - Get file info
- `GET /api/files/{id}/download` - Download file
- `DELETE /api/files/{id}` - Delete file

### WebSocket
- `WS /ws/experiments/{id}` - Real-time updates

## Project Structure

```
aide-backend/
├── main.py                 # FastAPI application
├── models.py               # Pydantic data models
├── websocket_manager.py    # WebSocket connection management
├── services/               # Business logic services
│   ├── experiment_service.py
│   └── file_service.py
├── uploads/                # File upload storage
├── experiments/            # Experiment data directories
├── static/                 # Static file serving
└── requirements.txt        # Python dependencies
```

## Integration with AIDE

The backend integrates directly with the existing AIDE ML engine:

- Imports `aide.Experiment` class
- Uses existing configuration and journal systems
- Maintains compatibility with current ML workflows
- Preserves all experiment tracking and visualization features

## Environment Variables

See `.env.example` for all available configuration options.

## Development Notes

- Uses async/await for non-blocking operations
- WebSocket connections managed per experiment
- File uploads stored locally with unique IDs
- Experiment results cached in memory
- Full error handling and validation
