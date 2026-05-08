from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from .db import Base

class AgentConfiguration(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    system_prompt = Column(String, nullable=False)
    llm_model = Column(String, default="gemini-1.5-flash-latest")  # Puede ser gemini, ollama:llama3.2:1b, claude
    temperature = Column(Integer, default=0.7)
    use_rag = Column(Boolean, default=False)
    has_code_interpreter = Column(Boolean, default=False)
    tools_enabled = Column(JSON, default=list) # Ejemplo: ["web_search", "mcp_github"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AgentDocument(Base):
    __tablename__ = "agent_documents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    chunk_count = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
