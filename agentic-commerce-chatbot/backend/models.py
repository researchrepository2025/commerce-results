"""
Data models for AG-UI protocol and agent communication
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Literal
from datetime import datetime
import uuid


class AGUIMessage(BaseModel):
    """AG-UI protocol message format"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: Literal['text', 'tool_call', 'ui_update', 'error', 'status']
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UIUpdate(BaseModel):
    """UI update instruction"""
    component: str
    action: Literal['update', 'refresh', 'append', 'replace']
    data: Any
    transition: Literal['immediate', 'smooth', 'fade'] = 'smooth'


class ToolCall(BaseModel):
    """Tool invocation details"""
    tool: str
    parameters: Dict[str, Any]
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class DashboardUpdate(BaseModel):
    """Dashboard update parameters"""
    segment: Literal['consumer', 'business', 'government']
    parameter: str
    value: float
    year: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "segment": "consumer",
                "parameter": "adoption_rate",
                "value": 0.25,
                "year": 2025
            }
        }


class MarketAnalysisRequest(BaseModel):
    """Market analysis request"""
    segment: str
    metrics: Optional[List[str]] = None
    compare_with: Optional[List[str]] = None
    time_range: Optional[Dict[str, int]] = None


class ChatMessage(BaseModel):
    """Chat message format"""
    role: Literal['user', 'assistant', 'system']
    content: str
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ConversationThread(BaseModel):
    """Conversation thread metadata"""
    thread_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)