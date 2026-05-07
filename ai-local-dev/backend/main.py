from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from core.db import get_db, engine, Base
from core import models, schemas
from core.agent_factory import create_agent_graph
from langchain_core.messages import HumanMessage

# Inicializar Base de Datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Factory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    input: str
    session_id: str = "default_session"

@app.get("/")
def root():
    return {"status": "AI Agent Factory running", "docs": "/docs"}

# --- ADMIN ENDPOINTS ---

@app.post("/api/v1/admin/agents", response_model=schemas.AgentResponse)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.AgentConfiguration(**agent.model_dump())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@app.get("/api/v1/admin/agents", response_model=List[schemas.AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    return db.query(models.AgentConfiguration).all()

@app.get("/api/v1/admin/agents/{agent_id}", response_model=schemas.AgentResponse)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.AgentConfiguration).filter(models.AgentConfiguration.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

# --- CHAT ENDPOINTS ---

@app.post("/api/v1/agent/{agent_id}/chat")
def chat_with_agent(agent_id: int, data: ChatInput, db: Session = Depends(get_db)):
    # 1. Recuperar la configuración del agente
    config = db.query(models.AgentConfiguration).filter(models.AgentConfiguration.id == agent_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # 2. Compilar el grafo de LangGraph dinámicamente
    graph = create_agent_graph(config)
    
    # TODO: Integrar persistencia (memory_manager.py) aquí usando config={"configurable": {"thread_id": data.session_id}}
    
    # 3. Invocar al grafo
    initial_state = {
        "messages": [HumanMessage(content=data.input)],
        "agent_id": agent_id,
        "context": ""
    }
    
    try:
        # Aquí se ejecutaría el grafo completo
        result = graph.invoke(initial_state)
        # Extraer el último mensaje de la respuesta
        last_message = result["messages"][-1].content
        return {"response": last_message, "agent": config.name}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error executing agent: {str(e)}")
