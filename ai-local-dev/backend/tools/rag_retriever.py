from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def get_qdrant_retriever(collection_name: str):
    """
    Configura y devuelve el retriever apuntando a la base de datos local Qdrant.
    Por defecto, Qdrant corre en localhost:6333 usando el docker-compose.
    """
    client = QdrantClient(url="http://localhost:6333")
    
    # Configuramos el modelo de embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    qdrant = Qdrant(client=client, collection_name=collection_name, embeddings=embeddings)
    
    # Devuelve el retriever con los top k resultados
    return qdrant.as_retriever(search_kwargs={"k": 5})

def retrieve_context(query: str, collection_name: str) -> str:
    """Busca contexto y lo formatea como un bloque de texto."""
    retriever = get_qdrant_retriever(collection_name)
    docs = retriever.invoke(query)
    return "\n\n".join([doc.page_content for doc in docs])
