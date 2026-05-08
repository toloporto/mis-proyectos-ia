# Parche de compatibilidad para versiones mixtas de LangChain
import langchain
if not hasattr(langchain, 'verbose'):
    langchain.verbose = False

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
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


# --- DOCUMENT ENDPOINTS ---

ALLOWED_TYPES = {"pdf", "docx", "txt"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

@app.post("/api/v1/agent/{agent_id}/documents", response_model=schemas.DocumentResponse)
async def upload_document(agent_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    agent = db.query(models.AgentConfiguration).filter(models.AgentConfiguration.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if not agent.use_rag:
        raise HTTPException(status_code=400, detail="Este agente no tiene RAG habilitado")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail=f"Tipo no soportado: .{ext}")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Archivo supera el límite de 20MB")

    try:
        from tools.rag_retriever import ingest_document
        chunk_count = ingest_document(file_bytes, file.filename, f"agent_{agent_id}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando documento: {str(e)}")

    doc = models.AgentDocument(
        agent_id=agent_id,
        filename=file.filename,
        file_size=len(file_bytes),
        chunk_count=chunk_count
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@app.get("/api/v1/agent/{agent_id}/documents", response_model=List[schemas.DocumentResponse])
def list_documents(agent_id: int, db: Session = Depends(get_db)):
    if not db.query(models.AgentConfiguration).filter(models.AgentConfiguration.id == agent_id).first():
        raise HTTPException(status_code=404, detail="Agent not found")
    return db.query(models.AgentDocument).filter(models.AgentDocument.agent_id == agent_id).all()


@app.delete("/api/v1/agent/{agent_id}/documents/{doc_id}", status_code=204)
def delete_document(agent_id: int, doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.AgentDocument).filter(
        models.AgentDocument.id == doc_id,
        models.AgentDocument.agent_id == agent_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return None
