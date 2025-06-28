"""
Data models for AIDE ML Backend API

Pydantic models for request/response validation and data serialization.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Generic type for API responses
T = TypeVar('T')

class ExperimentStatus(str, Enum):
    """Experiment status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"

class MetricValue(BaseModel):
    """Metric value with optional maximize flag."""
    value: Optional[float] = None
    maximize: Optional[bool] = None

class WorstMetricValue(MetricValue):
    """Worst metric value (always null)."""
    value: Optional[float] = None

class Node(BaseModel):
    """Solution step/node in the experiment tree."""
    id: str = Field(..., description="Unique node identifier")
    step: int = Field(..., description="Step number in the experiment")
    code: str = Field(..., description="Generated code for this step")
    plan: Optional[str] = Field(None, description="Plan or description for this step")
    parent_id: Optional[str] = Field(None, description="Parent node ID")
    children: List[str] = Field(default_factory=list, description="Child node IDs")
    
    # Execution information
    term_out: List[str] = Field(default_factory=list, description="Terminal output")
    exec_time: Optional[float] = Field(None, description="Execution time in seconds")
    exc_type: Optional[str] = Field(None, description="Exception type if error occurred")
    exc_info: Optional[Dict[str, Any]] = Field(None, description="Exception information")
    exc_stack: Optional[List[tuple]] = Field(None, description="Exception stack trace")
    
    # Evaluation
    analysis: Optional[str] = Field(None, description="Analysis of the step")
    metric: Optional[MetricValue] = Field(None, description="Performance metric")
    is_buggy: bool = Field(False, description="Whether this step has bugs")
    debug_depth: int = Field(0, description="Debug depth level")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Journal(BaseModel):
    """Experiment journal containing all nodes and history."""
    experiment_id: str = Field(..., description="Associated experiment ID")
    nodes: List[Node] = Field(default_factory=list, description="All experiment nodes")
    draft_nodes: List[Node] = Field(default_factory=list, description="Draft nodes")
    buggy_nodes: List[Node] = Field(default_factory=list, description="Buggy nodes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ExperimentConfig(BaseModel):
    """Experiment configuration and metadata."""
    id: str = Field(..., description="Unique experiment identifier")
    name: str = Field(..., description="Human-readable experiment name")
    data_dir: str = Field(..., description="Path to experiment data directory")
    goal: str = Field(..., description="Experiment objective")
    eval: Optional[str] = Field(None, description="Evaluation criteria")
    steps: int = Field(10, ge=1, le=50, description="Number of steps to run")
    
    # Status and progress
    status: ExperimentStatus = Field(ExperimentStatus.PENDING)
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress percentage (0-1)")
    current_step: int = Field(0, description="Current step number")
    
    # File associations
    files: List[str] = Field(default_factory=list, description="Associated file IDs")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None, description="When experiment started")
    completed_at: Optional[datetime] = Field(None, description="When experiment completed")

class ExperimentCreateRequest(BaseModel):
    """Request model for creating a new experiment."""
    name: str = Field(..., description="Experiment name")
    goal: str = Field(..., description="Experiment goal")
    eval: Optional[str] = Field(None, description="Evaluation criteria")
    steps: int = Field(10, ge=1, le=50, description="Number of steps")
    files: List[str] = Field(default_factory=list, description="File IDs to associate")

class ExperimentResults(BaseModel):
    """Experiment results and outputs."""
    experiment_id: str = Field(..., description="Experiment ID")
    status: ExperimentStatus = Field(..., description="Final status")
    
    best_solution: Optional[Dict[str, Any]] = Field(None, description="Best solution found")
    journal: Journal = Field(..., description="Complete experiment journal")
    tree_visualization: Optional[str] = Field(None, description="Tree visualization HTML")
    config: Dict[str, Any] = Field(default_factory=dict, description="Experiment configuration")
    
    # Performance metrics
    total_time: Optional[float] = Field(None, description="Total execution time")
    best_metric: Optional[MetricValue] = Field(None, description="Best metric achieved")
    
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

class UploadedFile(BaseModel):
    """Uploaded file metadata."""
    id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Stored filename")
    original_name: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    path: str = Field(..., description="File storage path")
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class ApiResponse(BaseModel, Generic[T]):
    """Generic API response wrapper."""
    success: bool = Field(..., description="Whether the operation was successful")
    data: Optional[T] = Field(None, description="Response data")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# WebSocket message types
class WebSocketMessage(BaseModel):
    """Base WebSocket message."""
    type: str = Field(..., description="Message type")
    experiment_id: str = Field(..., description="Associated experiment ID")

class ProgressUpdate(WebSocketMessage):
    """Progress update message."""
    type: str = Field("progress", description="Message type")
    data: Dict[str, Any] = Field(..., description="Progress data")

class StepComplete(WebSocketMessage):
    """Step completion message."""
    type: str = Field("step_complete", description="Message type")
    data: Dict[str, Any] = Field(..., description="Step completion data")

class ExperimentComplete(WebSocketMessage):
    """Experiment completion message."""
    type: str = Field("experiment_complete", description="Message type")
    data: Dict[str, Any] = Field(..., description="Completion data")

class ErrorNotification(WebSocketMessage):
    """Error notification message."""
    type: str = Field("error", description="Message type")
    data: Dict[str, Any] = Field(..., description="Error data")

# Response type aliases for better type hints
# Note: These will be created dynamically to avoid module loading issues
