from langgraph.checkpoint.memory import MemorySaver

# Checkpointer en memoria para desarrollo
dev_checkpointer = MemorySaver()

# Si quieres persistencia SQLite (opcional, requiere instalación de sqlite)
# from langgraph.checkpoint.sqlite import SqliteSaver
# db_checkpointer = SqliteSaver.from_conn_string("checkpoints.db")
