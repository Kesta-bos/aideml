"""Models package for AIDE ML Backend."""

from .config_models import *
from .validation_models import *
from .profile_models import *
from .template_models import *

# Import from the parent models.py file  
import sys
import importlib.util
from pathlib import Path

# Import from the parent directory models.py
parent_models_file = Path(__file__).parent.parent / "models.py"
if parent_models_file.exists():
    spec = importlib.util.spec_from_file_location("models_legacy", parent_models_file)
    models_legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(models_legacy)
    
    # Import necessary classes
    ApiResponse = models_legacy.ApiResponse
    ExperimentConfig = models_legacy.ExperimentConfig
    ExperimentCreateRequest = models_legacy.ExperimentCreateRequest
    ExperimentStatus = models_legacy.ExperimentStatus
    ExperimentResults = models_legacy.ExperimentResults
    UploadedFile = models_legacy.UploadedFile
    ErrorResponse = models_legacy.ErrorResponse
    WebSocketMessage = models_legacy.WebSocketMessage
    ProgressUpdate = models_legacy.ProgressUpdate
    StepComplete = models_legacy.StepComplete
    ExperimentComplete = models_legacy.ExperimentComplete
    ErrorNotification = models_legacy.ErrorNotification
    Journal = models_legacy.Journal
    Node = models_legacy.Node
    MetricValue = models_legacy.MetricValue