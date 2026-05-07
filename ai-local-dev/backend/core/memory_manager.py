import psycopg
from langgraph.checkpoint.postgres import PostgresSaver

# URL psycopg3 (langgraph usa psycopg3)
DB_URI = "postgresql://user:pass@localhost:5432/ai_db?sslmode=disable"

def get_checkpointer():
    """Inicializa y devuelve el Checkpointer de PostgreSQL para LangGraph."""
    # Usamos connection pooling si es necesario en producción, 
    # pero para local una conexión simple está bien.
    conn = psycopg.connect(DB_URI)
    
    checkpointer = PostgresSaver(conn)
    # Crea las tablas si no existen (langgraph_checkpoints, etc)
    checkpointer.setup()
    
    return checkpointer, conn
