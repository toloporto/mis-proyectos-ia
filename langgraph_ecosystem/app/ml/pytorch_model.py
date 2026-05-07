from langchain_core.tools import tool
from transformers import pipeline

class HuggingFaceSentimentTool:
    """Wrapper de un modelo de HuggingFace como herramienta LangChain."""
    def __init__(self):
        # Cargamos un modelo de análisis de sentimientos (alternativa ligera y potente)
        self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze(self, text: str) -> dict:
        result = self.sentiment_pipeline(text)[0]
        return {"tool": "SentimentAnalyzer", "text": text, "sentiment": result['label'], "score": result['score']}
