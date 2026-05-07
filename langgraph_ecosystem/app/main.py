from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.graph import app as graph_app
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

api = FastAPI(title="LangGraph Multi-Agent Ecosystem")

# Montar directorio de archivos estáticos
api.mount("/static", StaticFiles(directory="app/static"), name="static")

class ChatRequest(BaseModel):
    user_input: str
    thread_id: str = "default_thread"

@api.post("/chat")
def chat(request: ChatRequest):
    result = graph_app.invoke(
        {"messages": [HumanMessage(content=request.user_input)], "intermediate_results": {}, "iteration_count": 0},
        config={"configurable": {"thread_id": request.thread_id}}
    )
    # Extraemos el contenido del último mensaje
    last_msg = result["messages"][-1]
    response_content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
    return {"response": response_content}

@api.get("/")
def root():
    return FileResponse("app/static/index.html")
