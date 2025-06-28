"""
File Service

Handles file upload, storage, and management for experiments.
"""

import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import mimetypes

from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse

from models import UploadedFile

class FileService:
    """Service for managing file uploads and storage."""
    
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.files: Dict[str, UploadedFile] = {}
        
        # Allowed file types
        self.allowed_extensions = {'.csv', '.json', '.txt', '.zip', '.md', '.xlsx'}
        self.max_file_size = 100 * 1024 * 1024  # 100MB

    async def upload_multiple(self, files: List[UploadFile]) -> List[UploadedFile]:
        """Upload multiple files."""
        uploaded_files = []
        
        for file in files:
            uploaded_file = await self.upload_single(file)
            uploaded_files.append(uploaded_file)
        
        return uploaded_files

    async def upload_single(self, file: UploadFile) -> UploadedFile:
        """Upload a single file."""
        # Validate file
        await self._validate_file(file)
        
        # Generate unique file ID and filename
        file_id = f"file_{uuid.uuid4().hex[:12]}"
        file_extension = Path(file.filename).suffix.lower()
        stored_filename = f"{file_id}{file_extension}"
        file_path = self.upload_dir / stored_filename
        
        # Save file to disk
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
        # Get file info
        file_size = file_path.stat().st_size
        mime_type = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        
        # Create file record
        uploaded_file = UploadedFile(
            id=file_id,
            filename=stored_filename,
            original_name=file.filename,
            mime_type=mime_type,
            size=file_size,
            path=str(file_path),
            uploaded_at=datetime.utcnow()
        )
        
        # Store in memory
        self.files[file_id] = uploaded_file
        
        return uploaded_file

    async def get_info(self, file_id: str) -> UploadedFile:
        """Get file information."""
        if file_id not in self.files:
            raise ValueError(f"File {file_id} not found")
        
        return self.files[file_id]

    async def download(self, file_id: str) -> FileResponse:
        """Download a file."""
        if file_id not in self.files:
            raise ValueError(f"File {file_id} not found")
        
        file_info = self.files[file_id]
        file_path = Path(file_info.path)
        
        if not file_path.exists():
            raise ValueError(f"File {file_id} not found on disk")
        
        return FileResponse(
            path=str(file_path),
            filename=file_info.original_name,
            media_type=file_info.mime_type
        )

    async def delete(self, file_id: str):
        """Delete a file."""
        if file_id not in self.files:
            raise ValueError(f"File {file_id} not found")
        
        file_info = self.files[file_id]
        file_path = Path(file_info.path)
        
        # Remove from disk
        if file_path.exists():
            file_path.unlink()
        
        # Remove from memory
        del self.files[file_id]

    async def copy_to_experiment(self, file_ids: List[str], experiment_dir: Path):
        """Copy files to experiment directory."""
        experiment_dir.mkdir(parents=True, exist_ok=True)
        
        for file_id in file_ids:
            if file_id not in self.files:
                continue
            
            file_info = self.files[file_id]
            source_path = Path(file_info.path)
            dest_path = experiment_dir / file_info.original_name
            
            if source_path.exists():
                shutil.copy2(source_path, dest_path)

    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file."""
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_extension} not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        file_size = len(content)
        
        if file_size > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {self.max_file_size / (1024*1024):.1f}MB"
            )
        
        # Reset file pointer for later reading
        await file.seek(0)

    def list_files(self) -> List[UploadedFile]:
        """List all uploaded files."""
        return list(self.files.values())

    def get_file_stats(self) -> Dict[str, Any]:
        """Get file storage statistics."""
        total_files = len(self.files)
        total_size = sum(file_info.size for file_info in self.files.values())
        
        return {
            "totalFiles": total_files,
            "totalSize": total_size,
            "totalSizeMB": total_size / (1024 * 1024),
            "allowedExtensions": list(self.allowed_extensions),
            "maxFileSizeMB": self.max_file_size / (1024 * 1024)
        }
