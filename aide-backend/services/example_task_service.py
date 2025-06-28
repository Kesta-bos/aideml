"""
Example Task Service

Manages loading and serving example tasks from the AIDE codebase.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger("aide")


class ExampleTaskService:
    """Service for managing example tasks."""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the service.
        
        Args:
            base_path: Base path to the example tasks directory. 
                      If None, uses the default AIDE path.
        """
        if base_path:
            self.example_tasks_path = Path(base_path)
        else:
            # Default path relative to the current backend location
            current_dir = Path(__file__).parent.parent
            # Try different possible paths
            possible_paths = [
                current_dir / "aide" / "example_tasks",  # In Docker container
                current_dir.parent / "aide" / "example_tasks",  # Local development
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.example_tasks_path = path
                    break
            else:
                # Fallback to first path
                self.example_tasks_path = possible_paths[0]
        
        logger.info(f"Example tasks path: {self.example_tasks_path}")
    
    def _parse_markdown_task(self, md_file_path: Path) -> Dict[str, Any]:
        """
        Parse a markdown task file and extract metadata.
        
        Args:
            md_file_path: Path to the markdown file
            
        Returns:
            Dictionary with task metadata
        """
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract sections using regex
            sections = {}
            
            # Extract Goal
            goal_match = re.search(r'## Goal\s*\n(.*?)(?=\n##|\n$)', content, re.DOTALL)
            if goal_match:
                sections['goal'] = goal_match.group(1).strip()
            
            # Extract Background
            background_match = re.search(r'## Background\s*\n(.*?)(?=\n##|\n$)', content, re.DOTALL)
            if background_match:
                sections['background'] = background_match.group(1).strip()
            
            # Extract Evaluation
            eval_match = re.search(r'## Evaluation\s*\n(.*?)(?=\n##|\n$)', content, re.DOTALL)
            if eval_match:
                sections['evaluation'] = eval_match.group(1).strip()
            
            # Extract Evaluation metric
            metric_match = re.search(r'## Evaluation metric\s*\n(.*?)(?=\n##|\n$)', content, re.DOTALL)
            if metric_match:
                sections['evaluation_metric'] = metric_match.group(1).strip()
            
            # Extract Data description
            data_match = re.search(r'## Data description\s*\n(.*?)(?=\n##|\n$)', content, re.DOTALL)
            if data_match:
                sections['data_description'] = data_match.group(1).strip()
            
            return {
                'title': md_file_path.stem.replace('_', ' ').title(),
                'filename': md_file_path.name,
                'sections': sections
            }
            
        except Exception as e:
            logger.error(f"Error parsing markdown file {md_file_path}: {e}")
            return {}
    
    def _get_task_files(self, task_name: str) -> List[Dict[str, Any]]:
        """
        Get list of data files for a specific task.
        
        Args:
            task_name: Name of the task (directory name)
            
        Returns:
            List of file information dictionaries
        """
        task_dir = self.example_tasks_path / task_name
        if not task_dir.exists() or not task_dir.is_dir():
            return []
        
        files = []
        for file_path in task_dir.iterdir():
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    files.append({
                        'name': file_path.name,
                        'size': stat.st_size,
                        'type': file_path.suffix.lower().lstrip('.') or 'unknown',
                        'path': str(file_path.relative_to(self.example_tasks_path))
                    })
                except Exception as e:
                    logger.warning(f"Error getting file info for {file_path}: {e}")
        
        return sorted(files, key=lambda x: x['name'])
    
    async def list_example_tasks(self) -> List[Dict[str, Any]]:
        """
        List all available example tasks.
        
        Returns:
            List of example task information
        """
        if not self.example_tasks_path.exists():
            logger.warning(f"Example tasks directory does not exist: {self.example_tasks_path}")
            return []
        
        tasks = []
        
        try:
            for item in self.example_tasks_path.iterdir():
                if item.is_file() and item.suffix.lower() == '.md':
                    # This is a markdown task file
                    task_name = item.stem
                    task_info = self._parse_markdown_task(item)
                    
                    if task_info:
                        # Get associated data files
                        data_files = self._get_task_files(task_name)
                        
                        task_info.update({
                            'id': task_name,
                            'data_files': data_files,
                            'file_count': len(data_files),
                            'has_data': len(data_files) > 0
                        })
                        
                        tasks.append(task_info)
        
        except Exception as e:
            logger.error(f"Error listing example tasks: {e}")
            return []
        
        # Sort by title
        return sorted(tasks, key=lambda x: x.get('title', ''))
    
    async def get_example_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific example task.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task information dictionary or None if not found
        """
        md_file_path = self.example_tasks_path / f"{task_id}.md"
        
        if not md_file_path.exists():
            return None
        
        task_info = self._parse_markdown_task(md_file_path)
        if not task_info:
            return None
        
        # Get associated data files with content previews
        data_files = self._get_task_files(task_id)
        
        # Add content previews for small text files
        for file_info in data_files:
            file_path = self.example_tasks_path / file_info['path']
            
            # Add preview for small text files
            if (file_info['type'] in ['txt', 'md', 'csv'] and 
                file_info['size'] < 10000):  # Less than 10KB
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Limit preview to first 500 characters
                        file_info['preview'] = content[:500]
                        if len(content) > 500:
                            file_info['preview'] += '...'
                except Exception as e:
                    logger.warning(f"Error reading file preview for {file_path}: {e}")
        
        task_info.update({
            'id': task_id,
            'data_files': data_files,
            'file_count': len(data_files),
            'has_data': len(data_files) > 0
        })
        
        return task_info
    
    async def get_task_file_content(self, task_id: str, filename: str) -> Optional[bytes]:
        """
        Get the content of a specific file from an example task.
        
        Args:
            task_id: ID of the task
            filename: Name of the file to retrieve
            
        Returns:
            File content as bytes or None if not found
        """
        file_path = self.example_tasks_path / task_id / filename
        
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None