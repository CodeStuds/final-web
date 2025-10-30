#!/usr/bin/env python3
"""
Session Manager for HireSight
Handles session creation, management, and cleanup for job posting uploads
"""

import os
import json
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages upload sessions for job postings
    Each session has isolated storage for resumes, scores, and analyses
    """
    
    def __init__(self, base_upload_dir: str):
        """
        Initialize Session Manager
        
        Args:
            base_upload_dir: Base directory for all uploads (e.g., 'backend/uploads')
        """
        self.base_upload_dir = base_upload_dir
        os.makedirs(base_upload_dir, exist_ok=True)
        logger.info(f"Session Manager initialized with base dir: {base_upload_dir}")
    
    def create_session(
        self,
        company_id: Optional[str] = None,
        job_id: Optional[str] = None,
        job_title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str]:
        """
        Create a new session for a job posting
        
        Args:
            company_id: Company identifier (optional)
            job_id: Job posting identifier (optional)
            job_title: Job title (optional)
            metadata: Additional metadata to store
            
        Returns:
            tuple: (session_id, session_directory_path)
        """
        # Generate session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:19]  # Include microseconds
        
        # Build session ID components
        components = ['session']
        if company_id:
            components.append(self._sanitize_id(company_id))
        if job_id:
            components.append(self._sanitize_id(job_id))
        components.append(timestamp)
        
        session_id = '_'.join(components)
        session_dir = os.path.join(self.base_upload_dir, session_id)
        
        # Create directory structure
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(os.path.join(session_dir, 'reports'), exist_ok=True)
        os.makedirs(os.path.join(session_dir, 'resumes'), exist_ok=True)
        
        # Create metadata
        session_metadata = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'company_id': company_id or 'default',
            'job_id': job_id or 'default',
            'job_title': job_title or 'Unknown Position',
            'status': 'created',
            'candidates_processed': 0,
            'github_analyses_completed': 0,
            'linkedin_scores_generated': False
        }
        
        # Merge additional metadata
        if metadata:
            session_metadata.update(metadata)
        
        # Save metadata
        metadata_path = os.path.join(session_dir, 'metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(session_metadata, f, indent=2)
        
        logger.info(f"Created session: {session_id}")
        return session_id, session_dir
    
    def get_session_dir(self, session_id: str) -> str:
        """
        Get session directory path
        
        Args:
            session_id: Session identifier
            
        Returns:
            str: Path to session directory
            
        Raises:
            ValueError: If session doesn't exist
        """
        session_dir = os.path.join(self.base_upload_dir, session_id)
        if not os.path.exists(session_dir):
            raise ValueError(f"Session not found: {session_id}")
        return session_dir
    
    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """
        Load session metadata
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Session metadata
            
        Raises:
            ValueError: If session doesn't exist
        """
        session_dir = self.get_session_dir(session_id)
        metadata_path = os.path.join(session_dir, 'metadata.json')
        
        if not os.path.exists(metadata_path):
            raise ValueError(f"Session metadata not found: {session_id}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_session_metadata(
        self,
        session_id: str,
        updates: Dict[str, Any]
    ) -> None:
        """
        Update session metadata
        
        Args:
            session_id: Session identifier
            updates: Dictionary of fields to update
        """
        metadata = self.get_session_metadata(session_id)
        metadata.update(updates)
        metadata['updated_at'] = datetime.now().isoformat()
        
        session_dir = self.get_session_dir(session_id)
        metadata_path = os.path.join(session_dir, 'metadata.json')
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.debug(f"Updated metadata for session: {session_id}")
    
    def get_session_paths(self, session_id: str) -> Dict[str, str]:
        """
        Get all relevant paths for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Dictionary with paths (session_dir, reports_dir, resumes_dir, etc.)
        """
        session_dir = self.get_session_dir(session_id)
        
        return {
            'session_dir': session_dir,
            'reports_dir': os.path.join(session_dir, 'reports'),
            'resumes_dir': os.path.join(session_dir, 'resumes'),
            'results_csv': os.path.join(session_dir, 'results.csv'),
            'metadata_json': os.path.join(session_dir, 'metadata.json'),
            'leaderboard_json': os.path.join(session_dir, 'leaderboard.json')
        }
    
    def list_sessions(
        self,
        company_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all sessions, optionally filtered by company
        
        Args:
            company_id: Filter by company ID (optional)
            limit: Maximum number of sessions to return (optional)
            
        Returns:
            list: List of session metadata dictionaries
        """
        sessions = []
        
        # List all session directories
        for item in os.listdir(self.base_upload_dir):
            if item.startswith('session_'):
                try:
                    metadata = self.get_session_metadata(item)
                    
                    # Filter by company if specified
                    if company_id and metadata.get('company_id') != company_id:
                        continue
                    
                    sessions.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load session metadata for {item}: {e}")
                    continue
        
        # Sort by creation date (newest first)
        sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Apply limit if specified
        if limit:
            sessions = sessions[:limit]
        
        return sessions
    
    def cleanup_old_sessions(
        self,
        days: int = 7,
        dry_run: bool = False
    ) -> List[str]:
        """
        Clean up sessions older than specified days
        
        Args:
            days: Number of days to keep sessions (default: 7)
            dry_run: If True, only list sessions to delete without deleting
            
        Returns:
            list: List of deleted (or to-be-deleted) session IDs
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_sessions = []
        
        for item in os.listdir(self.base_upload_dir):
            if item.startswith('session_'):
                try:
                    metadata = self.get_session_metadata(item)
                    created_at = datetime.fromisoformat(metadata['created_at'])
                    
                    if created_at < cutoff_date:
                        if dry_run:
                            logger.info(f"Would delete session: {item} (created: {created_at})")
                        else:
                            session_dir = os.path.join(self.base_upload_dir, item)
                            shutil.rmtree(session_dir)
                            logger.info(f"Deleted old session: {item}")
                        
                        deleted_sessions.append(item)
                
                except Exception as e:
                    logger.warning(f"Failed to process session {item} for cleanup: {e}")
                    continue
        
        return deleted_sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            session_dir = self.get_session_dir(session_id)
            shutil.rmtree(session_dir)
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for all sessions
        
        Returns:
            dict: Storage statistics (total sessions, total size, etc.)
        """
        total_sessions = 0
        total_size = 0
        
        for item in os.listdir(self.base_upload_dir):
            if item.startswith('session_'):
                total_sessions += 1
                session_dir = os.path.join(self.base_upload_dir, item)
                
                # Calculate directory size
                for dirpath, dirnames, filenames in os.walk(session_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                        except OSError:
                            pass
        
        return {
            'total_sessions': total_sessions,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'base_directory': self.base_upload_dir
        }
    
    def _sanitize_id(self, id_string: str) -> str:
        """
        Sanitize ID string for use in filenames
        
        Args:
            id_string: Raw ID string
            
        Returns:
            str: Sanitized ID safe for filesystem
        """
        # Remove/replace unsafe characters
        safe_chars = []
        for char in id_string:
            if char.isalnum() or char in ['-', '_']:
                safe_chars.append(char)
            elif char in [' ', '.']:
                safe_chars.append('_')
        
        sanitized = ''.join(safe_chars)
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized.lower()


# Convenience function to create a session manager instance
def create_session_manager(upload_dir: str) -> SessionManager:
    """
    Create a SessionManager instance
    
    Args:
        upload_dir: Base upload directory
        
    Returns:
        SessionManager: Configured session manager
    """
    return SessionManager(upload_dir)
