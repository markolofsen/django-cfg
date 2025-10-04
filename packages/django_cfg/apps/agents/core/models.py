"""
Data models for Django Orchestrator.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


@dataclass
class ExecutionResult:
    """Result from agent execution with metadata."""
    
    agent_name: str
    output: Any
    execution_time: float
    tokens_used: int = 0
    cost: float = 0.0
    cached: bool = False
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.error is None


class WorkflowConfig(BaseModel):
    """Configuration for workflow execution."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    name: str = Field(..., description="Workflow identifier")
    timeout: int = Field(default=300, ge=1, le=3600, description="Timeout in seconds")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")
    execution_strategy: Literal["sequential", "parallel", "conditional"] = Field(
        default="sequential", description="Execution strategy"
    )
    priority: int = Field(default=1, ge=1, le=10, description="Execution priority")
    max_concurrent: int = Field(default=5, ge=1, le=20, description="Max concurrent executions")


class AgentDefinition(BaseModel):
    """Agent definition for registry storage."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    name: str = Field(..., description="Agent identifier")
    instructions: str = Field(..., description="Agent instructions")
    deps_type: str = Field(..., description="Dependencies type name")
    output_type: str = Field(..., description="Output type name")
    model: str = Field(default="openai:gpt-4o-mini", description="LLM model to use")
    timeout: int = Field(default=300, ge=1, le=3600, description="Execution timeout")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retries")
    is_active: bool = Field(default=True, description="Whether agent is active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProcessResult(BaseModel):
    """Standard processing result model."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    success: bool = Field(..., description="Whether processing was successful")
    message: str = Field(..., description="Result message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    timestamp: datetime = Field(default_factory=datetime.now)


class AnalysisResult(BaseModel):
    """Standard analysis result model."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    sentiment: str = Field(..., description="Sentiment analysis result")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    topics: List[str] = Field(default_factory=list, description="Extracted topics")
    keywords: List[str] = Field(default_factory=list, description="Key terms")
    summary: str = Field(default="", description="Content summary")


class ValidationResult(BaseModel):
    """Standard validation result model."""
    
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    is_valid: bool = Field(..., description="Whether input is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")


@dataclass
class ErrorContext:
    """Error context information."""
    
    agent_name: str
    prompt: str
    error_type: str
    error_message: str
    timestamp: datetime
    retry_count: int = 0
    stack_trace: Optional[str] = None
