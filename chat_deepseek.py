from openai import OpenAI
import sys

# Configuración del cliente local
client = OpenAI(
    base_url='http://localhost:11434/v1',
    api_key='ollama', 
)

def chat():
    print("--- Bienvenido a tu Chat con DeepSeek (Local) ---")
    print("Escribe 'salir' para terminar.\n")
    
    while True:
        prompt = input("Tú: ")
        if prompt.lower() in ["salir", "exit", "quit"]:
            break
            
        try:
            response = client.chat.completions.create(
                model="deepseek-coder-v2", # O el modelo que tengas en Ollama
                messages=[{"role": "user", "content": prompt}],
                stream=True # Activamos el modo streaming para ver cómo "escribe" la IA
            )
            
            print("DeepSeek: ", end="", flush=True)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    print(chunk.choices[0].delta.content, end="", flush=True)
            print("\n")
            
        except Exception as e:
            print(f"\n[Error] No se pudo conectar con Ollama: {e}")
            break

if __name__ == "__main__":
    chat()
