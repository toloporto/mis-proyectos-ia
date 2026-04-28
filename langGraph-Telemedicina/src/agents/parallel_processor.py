# src/agents/parallel_processor.py
import asyncio
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class ParallelAgentProcessor:
    """Ejecuta agentes en paralelo cuando es posible"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    async def ejecutar_en_paralelo(self, tareas: List[Dict]) -> Dict[str, Any]:
        """Ejecuta múltiples agentes simultáneamente"""
        loop = asyncio.get_event_loop()
        
        # Crear tareas asíncronas
        tareas_async = []
        for tarea in tareas:
            tareas_async.append(
                loop.run_in_executor(
                    self.executor,
                    tarea['funcion'],
                    tarea['prompt']
                )
            )
        
        # Ejecutar en paralelo
        resultados = await asyncio.gather(*tareas_async, return_exceptions=True)
        
        # Procesar resultados
        return {tareas[i]['nombre']: resultados[i] for i in range(len(tareas))}