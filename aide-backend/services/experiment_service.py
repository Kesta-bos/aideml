"""
Experiment Service

Handles experiment lifecycle management, execution, and result collection.
"""

import asyncio
import uuid
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import (
    ExperimentConfig, 
    ExperimentCreateRequest, 
    ExperimentStatus, 
    ExperimentResults,
    Journal,
    Node,
    MetricValue
)

# Import AIDE experiment class
import sys
import os
from pathlib import Path

# Add the parent directory to Python path to import AIDE
current_dir = Path(__file__).parent
aide_root = current_dir.parent.parent
sys.path.insert(0, str(aide_root))

try:
    from aide import Experiment as AIDEExperiment
except ImportError as e:
    print(f"Warning: Could not import AIDE Experiment: {e}")
    # Create a mock class for development
    class AIDEExperiment:
        def __init__(self, data_dir, goal, eval=None):
            self.data_dir = data_dir
            self.goal = goal
            self.eval = eval
            self.journal = MockJournal()
            self.cfg = MockConfig()

        def run(self, steps=1):
            # Mock implementation
            import time
            time.sleep(1)  # Simulate work

    class MockJournal:
        def __init__(self):
            self.nodes = []

        def get_best_node(self, only_good=False):
            return MockNode()

    class MockConfig:
        def __init__(self):
            self.log_dir = Path("./mock_logs")
            self.log_dir.mkdir(exist_ok=True)

    class MockNode:
        def __init__(self):
            self.id = "mock_node_1"
            self.step = 1
            self.code = "# Mock generated code\nprint('Hello from AIDE!')"
            self.metric = MockMetric()
            self.is_buggy = False
            self.exec_time = 1.5

    class MockMetric:
        def __init__(self):
            self.value = 0.85
            self.maximize = True

class ExperimentService:
    """Service for managing ML experiments."""
    
    def __init__(self):
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.running_experiments: Dict[str, asyncio.Task] = {}
        self.experiment_results: Dict[str, ExperimentResults] = {}
        
        # Create experiments directory
        self.experiments_dir = Path("experiments")
        self.experiments_dir.mkdir(exist_ok=True)

    async def create(self, request: ExperimentCreateRequest) -> ExperimentConfig:
        """Create a new experiment."""
        experiment_id = f"exp_{uuid.uuid4().hex[:12]}"
        
        # Create experiment data directory
        data_dir = self.experiments_dir / experiment_id / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy uploaded files to experiment directory
        if request.files:
            await self._copy_files_to_experiment(request.files, data_dir)
        
        experiment = ExperimentConfig(
            id=experiment_id,
            name=request.name,
            goal=request.goal,
            eval=request.eval,
            steps=request.steps,
            data_dir=str(data_dir),
            files=request.files,
            status=ExperimentStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.experiments[experiment_id] = experiment
        return experiment

    async def get(self, experiment_id: str) -> ExperimentConfig:
        """Get experiment by ID."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        return self.experiments[experiment_id]

    async def start(self, experiment_id: str, websocket_manager):
        """Start experiment execution."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        if experiment.status == ExperimentStatus.RUNNING:
            raise ValueError("Experiment is already running")
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.started_at = datetime.utcnow()
        experiment.updated_at = datetime.utcnow()
        
        # Start experiment in background
        task = asyncio.create_task(
            self._run_experiment(experiment, websocket_manager)
        )
        self.running_experiments[experiment_id] = task

    async def stop(self, experiment_id: str):
        """Stop experiment execution."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if experiment_id in self.running_experiments:
            task = self.running_experiments[experiment_id]
            task.cancel()
            del self.running_experiments[experiment_id]
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.STOPPED
        experiment.updated_at = datetime.utcnow()

    async def get_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment status."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        experiment = self.experiments[experiment_id]
        return {
            "id": experiment.id,
            "status": experiment.status,
            "progress": experiment.progress,
            "currentStep": experiment.current_step,
            "totalSteps": experiment.steps,
            "createdAt": experiment.created_at,
            "updatedAt": experiment.updated_at,
            "startedAt": experiment.started_at,
            "completedAt": experiment.completed_at
        }

    async def get_results(self, experiment_id: str) -> ExperimentResults:
        """Get experiment results."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        if experiment_id not in self.experiment_results:
            raise ValueError("Experiment results not available yet")
        
        return self.experiment_results[experiment_id]

    async def delete(self, experiment_id: str):
        """Delete an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        # Stop if running
        if experiment_id in self.running_experiments:
            await self.stop(experiment_id)
        
        # Remove experiment directory
        experiment_dir = self.experiments_dir / experiment_id
        if experiment_dir.exists():
            shutil.rmtree(experiment_dir)
        
        # Remove from memory
        del self.experiments[experiment_id]
        if experiment_id in self.experiment_results:
            del self.experiment_results[experiment_id]

    async def list(self, page: int = 1, limit: int = 10, status: Optional[str] = None) -> Dict[str, Any]:
        """List experiments with pagination."""
        experiments = list(self.experiments.values())
        
        # Filter by status if provided
        if status:
            experiments = [exp for exp in experiments if exp.status == status]
        
        # Sort by creation date (newest first)
        experiments.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_experiments = experiments[start:end]
        
        return {
            "experiments": paginated_experiments,
            "total": len(experiments),
            "page": page,
            "limit": limit,
            "totalPages": (len(experiments) + limit - 1) // limit
        }

    async def _copy_files_to_experiment(self, file_ids: List[str], data_dir: Path):
        """Copy uploaded files to experiment data directory."""
        from .file_service import FileService

        # Create a temporary file service instance to access uploaded files
        upload_dir = Path("uploads")
        file_service = FileService(upload_dir)

        # Copy each file to the experiment directory
        for file_id in file_ids:
            try:
                await file_service.copy_to_experiment([file_id], data_dir)
            except Exception as e:
                print(f"Warning: Could not copy file {file_id}: {e}")
                continue

    async def _run_experiment(self, experiment: ExperimentConfig, websocket_manager):
        """Run the AIDE experiment with progress updates."""
        try:
            # Initialize AIDE experiment
            aide_experiment = AIDEExperiment(
                data_dir=experiment.data_dir,
                goal=experiment.goal,
                eval=experiment.eval
            )
            
            # Run experiment with progress updates
            for step in range(experiment.steps):
                current_step = step + 1
                progress = current_step / experiment.steps
                
                # Update experiment state
                experiment.current_step = current_step
                experiment.progress = progress
                experiment.updated_at = datetime.utcnow()
                
                # Send progress update
                await websocket_manager.send_to_experiment(
                    experiment.id,
                    {
                        "type": "progress",
                        "data": {
                            "experimentId": experiment.id,
                            "currentStep": current_step,
                            "totalSteps": experiment.steps,
                            "progress": progress,
                            "status": "running"
                        }
                    }
                )
                
                # Run one step
                aide_experiment.run(steps=1)
                
                # Get current best node for step completion update
                if aide_experiment.journal.nodes:
                    latest_node = aide_experiment.journal.nodes[-1]
                    
                    # Send step completion
                    await websocket_manager.send_to_experiment(
                        experiment.id,
                        {
                            "type": "step_complete",
                            "data": {
                                "experimentId": experiment.id,
                                "step": current_step,
                                "node": {
                                    "id": latest_node.id,
                                    "code": latest_node.code,
                                    "metric": {
                                        "value": latest_node.metric.value if latest_node.metric else None,
                                        "maximize": latest_node.metric.maximize if latest_node.metric else None
                                    },
                                    "isBuggy": latest_node.is_buggy,
                                    "execTime": latest_node.exec_time
                                }
                            }
                        }
                    )
            
            # Experiment completed successfully
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            experiment.progress = 1.0
            
            # Collect and store results
            results = await self._collect_results(experiment, aide_experiment)
            self.experiment_results[experiment.id] = results
            
            # Send completion notification
            await websocket_manager.send_to_experiment(
                experiment.id,
                {
                    "type": "experiment_complete",
                    "data": {
                        "experimentId": experiment.id,
                        "status": "completed",
                        "results": results.dict()
                    }
                }
            )
            
        except asyncio.CancelledError:
            # Experiment was cancelled
            experiment.status = ExperimentStatus.STOPPED
            experiment.updated_at = datetime.utcnow()
            
        except Exception as e:
            # Experiment failed
            experiment.status = ExperimentStatus.FAILED
            experiment.updated_at = datetime.utcnow()
            
            await websocket_manager.send_to_experiment(
                experiment.id,
                {
                    "type": "error",
                    "data": {
                        "experimentId": experiment.id,
                        "error": "EXECUTION_ERROR",
                        "message": str(e),
                        "details": {"exception": type(e).__name__}
                    }
                }
            )
        finally:
            # Clean up
            if experiment.id in self.running_experiments:
                del self.running_experiments[experiment.id]

    async def _collect_results(self, experiment: ExperimentConfig, aide_experiment) -> ExperimentResults:
        """Collect results from completed experiment."""
        # Get best solution
        best_node = aide_experiment.journal.get_best_node(only_good=False)
        best_solution = None
        
        if best_node:
            best_solution = {
                "code": best_node.code,
                "metric": {
                    "value": best_node.metric.value if best_node.metric else None,
                    "maximize": best_node.metric.maximize if best_node.metric else None
                }
            }
        
        # Convert journal nodes
        journal_nodes = []
        for node in aide_experiment.journal.nodes:
            journal_nodes.append(Node(
                id=node.id,
                step=node.step,
                code=node.code,
                plan=getattr(node, 'plan', None),
                parent_id=getattr(node, 'parent_id', None),
                children=getattr(node, 'children', []),
                term_out=getattr(node, 'term_out', []),
                exec_time=getattr(node, 'exec_time', None),
                exc_type=getattr(node, 'exc_type', None),
                exc_info=getattr(node, 'exc_info', None),
                exc_stack=getattr(node, 'exc_stack', None),
                analysis=getattr(node, 'analysis', None),
                metric=MetricValue(
                    value=node.metric.value if node.metric else None,
                    maximize=node.metric.maximize if node.metric else None
                ) if node.metric else None,
                is_buggy=getattr(node, 'is_buggy', False),
                debug_depth=getattr(node, 'debug_depth', 0),
                created_at=datetime.utcnow()
            ))
        
        journal = Journal(
            experiment_id=experiment.id,
            nodes=journal_nodes,
            created_at=experiment.created_at,
            updated_at=datetime.utcnow()
        )
        
        # Get tree visualization if available
        tree_path = Path(aide_experiment.cfg.log_dir) / "tree_plot.html"
        tree_visualization = None
        if tree_path.exists():
            tree_visualization = tree_path.read_text(encoding='utf-8')
        
        return ExperimentResults(
            experiment_id=experiment.id,
            status=experiment.status,
            best_solution=best_solution,
            journal=journal,
            tree_visualization=tree_visualization,
            config=aide_experiment.cfg.__dict__ if hasattr(aide_experiment.cfg, '__dict__') else {},
            total_time=(experiment.completed_at - experiment.started_at).total_seconds() if experiment.completed_at and experiment.started_at else None,
            best_metric=MetricValue(
                value=best_node.metric.value if best_node and best_node.metric else None,
                maximize=best_node.metric.maximize if best_node and best_node.metric else None
            ) if best_node and best_node.metric else None,
            completed_at=experiment.completed_at
        )
