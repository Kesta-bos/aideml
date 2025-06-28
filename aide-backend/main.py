"""
AIDE ML Backend API

FastAPI backend for the AIDE Machine Learning Engineer Agent.
Provides REST API endpoints and WebSocket support for the React frontend.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, HTMLResponse
import uvicorn
import logging
from typing import List, Dict, Any
import os
import json
import asyncio
from pathlib import Path

from models import (
    ExperimentConfig, 
    ExperimentCreateRequest,
    ApiResponse,
    UploadedFile
)
from services.experiment_service import ExperimentService
from services.file_service import FileService
from services.api_key_service import ApiKeyService, ApiKeyValidationError
from services.example_task_service import ExampleTaskService
from services.visualization_service import VisualizationService
from websocket_manager import WebSocketManager

# Setup logging
logger = logging.getLogger("aide")

# Initialize FastAPI app
app = FastAPI(
    title="AIDE ML API",
    description="API for AIDE Machine Learning Agent",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)

# Static files for serving visualizations
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
experiment_service = ExperimentService()
file_service = FileService(upload_dir)
api_key_service = ApiKeyService()
example_task_service = ExampleTaskService()
visualization_service = VisualizationService()
websocket_manager = WebSocketManager()

# Import and include routers
from routers.config_router import router as config_router
from routers.profile_router import router as profile_router
app.include_router(config_router)
app.include_router(profile_router)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AIDE ML API",
        "version": "2.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "aide-ml-api"}

# Experiment endpoints
@app.post("/api/experiments")
async def create_experiment(request: ExperimentCreateRequest):
    """Create a new experiment."""
    try:
        experiment = await experiment_service.create(request)
        return ApiResponse(
            success=True,
            data=experiment,
            message="Experiment created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/experiments/{experiment_id}")
async def get_experiment(experiment_id: str):
    """Get experiment details."""
    try:
        experiment = await experiment_service.get(experiment_id)
        return ApiResponse(
            success=True,
            data=experiment,
            message="Experiment retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start experiment execution."""
    try:
        await experiment_service.start(experiment_id, websocket_manager)
        return ApiResponse(
            success=True,
            data={"id": experiment_id, "status": "running"},
            message="Experiment started successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/experiments/{experiment_id}/stop")
async def stop_experiment(experiment_id: str):
    """Stop experiment execution."""
    try:
        await experiment_service.stop(experiment_id)
        return ApiResponse(
            success=True,
            data={"id": experiment_id, "status": "stopped"},
            message="Experiment stopped successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/experiments/{experiment_id}/status")
async def get_experiment_status(experiment_id: str):
    """Get current experiment status."""
    try:
        status = await experiment_service.get_status(experiment_id)
        return ApiResponse(
            success=True,
            data=status,
            message="Status retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str):
    """Get experiment results and journal."""
    try:
        results = await experiment_service.get_results(experiment_id)
        return ApiResponse(
            success=True,
            data=results,
            message="Results retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str):
    """Delete an experiment."""
    try:
        await experiment_service.delete(experiment_id)
        return ApiResponse(
            success=True,
            data={"id": experiment_id},
            message="Experiment deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/experiments")
async def list_experiments(page: int = 1, limit: int = 10, status: str = None):
    """List experiments with pagination."""
    try:
        experiments = await experiment_service.list(page, limit, status)
        return ApiResponse(
            success=True,
            data=experiments,
            message="Experiments retrieved successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# File management endpoints
@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload experiment data files."""
    try:
        uploaded_files = await file_service.upload_multiple(files)
        return ApiResponse(
            success=True,
            data=uploaded_files,
            message=f"{len(uploaded_files)} files uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/files/{file_id}")
async def get_file_info(file_id: str):
    """Get file information."""
    try:
        file_info = await file_service.get_info(file_id)
        return ApiResponse(
            success=True,
            data=file_info,
            message="File info retrieved successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Download a specific file."""
    try:
        return await file_service.download(file_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete an uploaded file."""
    try:
        await file_service.delete(file_id)
        return ApiResponse(
            success=True,
            data={"id": file_id},
            message="File deleted successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Configuration endpoints
@app.get("/api/config")
async def get_config():
    """Get application configuration."""
    config = {
        "maxFileSize": 100 * 1024 * 1024,  # 100MB
        "allowedFileTypes": ["csv", "json", "txt", "zip", "md"],
        "maxExperimentSteps": 50,
        "supportedModels": ["gpt-4", "claude-3", "gpt-3.5-turbo"]
    }
    return ApiResponse(
        success=True,
        data=config,
        message="Configuration retrieved successfully"
    )

@app.post("/api/config/validate-api-key")
async def validate_api_key(request: Dict[str, str]):
    """Validate API key for external services."""
    try:
        provider = request.get("provider")
        api_key = request.get("apiKey")
        
        if not provider or not api_key:
            raise HTTPException(status_code=400, detail="Provider and apiKey are required")
        
        # Use the actual API key validation service
        validation_result = await api_key_service.validate_api_key(provider, api_key)
        
        return ApiResponse(
            success=validation_result["valid"],
            data=validation_result,
            message=validation_result["message"]
        )
        
    except ApiKeyValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in API key validation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during validation")

# Example tasks endpoints
@app.get("/api/example-tasks")
async def list_example_tasks():
    """List all available example tasks."""
    try:
        tasks = await example_task_service.list_example_tasks()
        return ApiResponse(
            success=True,
            data=tasks,
            message=f"Found {len(tasks)} example tasks"
        )
    except Exception as e:
        logger.error(f"Error listing example tasks: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving example tasks")

@app.get("/api/example-tasks/{task_id}")
async def get_example_task(task_id: str):
    """Get detailed information about a specific example task."""
    try:
        task = await example_task_service.get_example_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail=f"Example task '{task_id}' not found")
        
        return ApiResponse(
            success=True,
            data=task,
            message="Example task retrieved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting example task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving example task")

@app.get("/api/example-tasks/{task_id}/files/{filename}")
async def download_example_task_file(task_id: str, filename: str):
    """Download a specific file from an example task."""
    try:
        file_content = await example_task_service.get_task_file_content(task_id, filename)
        if file_content is None:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found in task '{task_id}'")
        
        # Determine content type based on file extension
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        return Response(
            content=file_content,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {filename} from task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Error downloading file")

# Visualization endpoints
@app.get("/api/experiments/{experiment_id}/tree-visualization", response_class=HTMLResponse)
async def get_tree_visualization(experiment_id: str):
    """Get tree visualization HTML for an experiment."""
    try:
        html = await visualization_service.get_experiment_tree_html(experiment_id)
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Error generating tree visualization for {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating visualization")

@app.get("/api/visualizations/demo-tree", response_class=HTMLResponse)
async def get_demo_tree_visualization():
    """Get demo tree visualization HTML."""
    try:
        html = visualization_service.generate_tree_visualization_html()
        return HTMLResponse(content=html)
    except Exception as e:
        logger.error(f"Error generating demo tree visualization: {e}")
        raise HTTPException(status_code=500, detail="Error generating demo visualization")

# WebSocket endpoint
@app.websocket("/ws/experiments/{experiment_id}")
async def websocket_endpoint(websocket: WebSocket, experiment_id: str):
    """WebSocket endpoint for real-time experiment updates."""
    await websocket_manager.connect(websocket, experiment_id)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
