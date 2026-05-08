from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AgentBase(BaseModel):
    name: str = Field(..., description="Nombre del agente (ej. 'Asesor Legal')")
    role: str = Field(..., description="Rol principal del agente")
    system_prompt: str = Field(..., description="Prompt del sistema que define su comportamiento")
    llm_model: str = Field(default="gemini-1.5-flash-latest")
    temperature: float = Field(default=0.7)
    use_rag: bool = Field(default=False)
    has_code_interpreter: bool = Field(default=False)
    tools_enabled: List[str] = Field(default_factory=list)

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    role: Optional[str] = None
    system_prompt: Optional[str] = None

class AgentResponse(AgentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    agent_id: int
    filename: str
    file_size: int
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
