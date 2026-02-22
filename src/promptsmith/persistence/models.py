"""Database Models for reasoning trace persistence."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ReasoningLogDB(Base):
    """SQLAlchemy model for reasoning logs."""
    
    __tablename__ = "reasoning_logs"
    
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    task_input = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    detected_category = Column(String(50), nullable=False)
    complexity_score = Column(Float, nullable=False)
    selected_framework = Column(String(50), nullable=False)
    meta_prompt_generated = Column(Text, nullable=False)
    execution_feedback = Column(Text, nullable=True)


# Pydantic models for API
class ReasoningLogCreate(BaseModel):
    """Input model for creating a reasoning log."""
    
    task_input: str = Field(..., description="The original task text")
    context: Optional[str] = Field(None, description="Additional context provided")
    detected_category: str = Field(..., description="Detected task category")
    complexity_score: float = Field(..., ge=0, le=10, description="Complexity score")
    selected_framework: str = Field(..., description="Framework used for prompt generation")
    meta_prompt_generated: str = Field(..., description="The generated meta-prompt")


class ReasoningLog(BaseModel):
    """Full reasoning log model for API responses."""
    
    id: UUID = Field(default_factory=uuid4, description="Unique log ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When this was logged")
    task_input: str = Field(..., description="The original task text")
    context: Optional[str] = Field(None, description="Additional context provided")
    detected_category: str = Field(..., description="Detected task category")
    complexity_score: float = Field(..., ge=0, le=10, description="Complexity score")
    selected_framework: str = Field(..., description="Framework used for prompt generation")
    meta_prompt_generated: str = Field(..., description="The generated meta-prompt")
    execution_feedback: Optional[str] = Field(None, description="Feedback after execution")
    
    model_config = ConfigDict(from_attributes=True)
