"""Database Storage Operations."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, ReasoningLogDB, ReasoningLog, ReasoningLogCreate
from promptcore.utils.safe_files import SafeFileManager


class Storage:
    """SQLite storage for reasoning logs."""
    
    def __init__(self, db_url: str):
        """
        Initialize storage.
        
        Args:
            db_url: SQLAlchemy database URL (e.g. sqlite:///path/to/db)
        """
        self.db_url = db_url
        connect_args = {}
        poolclass = None
        
        if ":memory:" in self.db_url:
            from sqlalchemy.pool import StaticPool
            connect_args = {"check_same_thread": False}
            poolclass = StaticPool

        self.engine = create_engine(
            self.db_url, 
            echo=False,
            connect_args=connect_args,
            poolclass=poolclass
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
        
    def initialize(self):
        """Create tables and ensure directory structure exists."""
        if self.db_url.startswith("sqlite:///"):
            # Extract path from URL for directory creation if it's a file
            path_str = self.db_url.replace("sqlite:///", "")
            if path_str != ":memory:":
                db_path = Path(path_str)
                # Use SafeFileManager for safe directory creation
                SafeFileManager.ensure_directory(db_path.parent)
                
        Base.metadata.create_all(self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def create_log(self, log_data: ReasoningLogCreate) -> ReasoningLog:
        """
        Create a new reasoning log entry.
        
        Args:
            log_data: The log data to persist
        
        Returns:
            The created ReasoningLog with ID and timestamp
        """
        log_id = str(uuid4())
        timestamp = datetime.utcnow()
        
        db_log = ReasoningLogDB(
            id=log_id,
            timestamp=timestamp,
            task_input=log_data.task_input,
            context=log_data.context,
            detected_category=log_data.detected_category,
            complexity_score=log_data.complexity_score,
            selected_framework=log_data.selected_framework,
            meta_prompt_generated=log_data.meta_prompt_generated,
            execution_feedback=None,
        )
        
        with self._get_session() as session:
            session.add(db_log)
            session.commit()
            session.refresh(db_log)
            
            return ReasoningLog(
                id=log_id,
                timestamp=timestamp,
                task_input=db_log.task_input,
                context=db_log.context,
                detected_category=db_log.detected_category,
                complexity_score=db_log.complexity_score,
                selected_framework=db_log.selected_framework,
                meta_prompt_generated=db_log.meta_prompt_generated,
                execution_feedback=db_log.execution_feedback,
            )
    
    def get_log(self, log_id: str) -> Optional[ReasoningLog]:
        """
        Retrieve a reasoning log by ID.
        
        Args:
            log_id: The UUID of the log to retrieve
        
        Returns:
            The ReasoningLog if found, None otherwise
        """
        with self._get_session() as session:
            db_log = session.query(ReasoningLogDB).filter(
                ReasoningLogDB.id == str(log_id)
            ).first()
            
            if not db_log:
                return None
            
            return ReasoningLog(
                id=db_log.id,
                timestamp=db_log.timestamp,
                task_input=db_log.task_input,
                context=db_log.context,
                detected_category=db_log.detected_category,
                complexity_score=db_log.complexity_score,
                selected_framework=db_log.selected_framework,
                meta_prompt_generated=db_log.meta_prompt_generated,
                execution_feedback=db_log.execution_feedback,
            )
    
    def update_feedback(self, log_id: str, feedback: str) -> Optional[ReasoningLog]:
        """
        Update the execution feedback for a log entry.
        
        Args:
            log_id: The UUID of the log to update
            feedback: The feedback text to add
        
        Returns:
            The updated ReasoningLog if found, None otherwise
        """
        with self._get_session() as session:
            db_log = session.query(ReasoningLogDB).filter(
                ReasoningLogDB.id == str(log_id)
            ).first()
            
            if not db_log:
                return None
            
            db_log.execution_feedback = feedback
            session.commit()
            session.refresh(db_log)
            
            return ReasoningLog(
                id=db_log.id,
                timestamp=db_log.timestamp,
                task_input=db_log.task_input,
                context=db_log.context,
                detected_category=db_log.detected_category,
                complexity_score=db_log.complexity_score,
                selected_framework=db_log.selected_framework,
                meta_prompt_generated=db_log.meta_prompt_generated,
                execution_feedback=db_log.execution_feedback,
            )
    
    def list_logs(self, limit: int = 100, offset: int = 0) -> list[ReasoningLog]:
        """
        List reasoning logs with pagination.
        
        Args:
            limit: Maximum number of logs to return
            offset: Number of logs to skip
        
        Returns:
            List of ReasoningLog entries
        """
        with self._get_session() as session:
            db_logs = session.query(ReasoningLogDB).order_by(
                ReasoningLogDB.timestamp.desc()
            ).offset(offset).limit(limit).all()
            
            return [
                ReasoningLog(
                    id=log.id,
                    timestamp=log.timestamp,
                    task_input=log.task_input,
                    context=log.context,
                    detected_category=log.detected_category,
                    complexity_score=log.complexity_score,
                    selected_framework=log.selected_framework,
                    meta_prompt_generated=log.meta_prompt_generated,
                    execution_feedback=log.execution_feedback,
                )
                for log in db_logs
            ]
    
    def get_stats(self) -> dict:
        """
        Get usage statistics.
        
        Returns:
            Dictionary with statistics about reasoning logs
        """
        with self._get_session() as session:
            total = session.query(ReasoningLogDB).count()
            
            # Count by framework
            from sqlalchemy import func
            framework_counts = session.query(
                ReasoningLogDB.selected_framework,
                func.count(ReasoningLogDB.id)
            ).group_by(ReasoningLogDB.selected_framework).all()
            
            # Count by category
            category_counts = session.query(
                ReasoningLogDB.detected_category,
                func.count(ReasoningLogDB.id)
            ).group_by(ReasoningLogDB.detected_category).all()
            
            # Average complexity
            avg_complexity = session.query(
                func.avg(ReasoningLogDB.complexity_score)
            ).scalar() or 0.0
            
            return {
                "total_logs": total,
                "by_framework": dict(framework_counts),
                "by_category": dict(category_counts),
                "average_complexity": round(avg_complexity, 2),
            }
