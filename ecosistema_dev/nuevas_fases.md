# Plan de Evolución: Ecosistema Nexus v4.0

Este plan detalla la expansión del ecosistema hacia servicios integrales (Seguros/Farmacia), gestión de sesiones persistentes y visión multimodal real.

## Fase 4: Especialistas en Seguros y Farmacia
**Objetivo:** Añadir dos nuevos nodos al grafo para cerrar el círculo de atención al cliente.

### [NEW] `agente_seguros.py` y `agente_farmacia.py`
- **Agente Seguros:** Analiza si el riesgo médico detectado está cubierto por la póliza del usuario.
- **Agente Farmacia:** Recomienda medicación base (con disclaimers) basándose en el informe médico.
- **Grafo:** El flujo se extenderá: `Medico -> Financiero -> Seguros -> Farmacia -> Síntesis`.

---

## Fase 5: UI de Historial Dinámica
**Objetivo:** Que el menú lateral (Sidebar) sea funcional y permita cargar consultas antiguas.

### [MODIFY] [orquestador.py](file:///home/toloporto/proyectos/ecosistema_dev/orquestador.py)
- **Nuevo Endpoint `/sesiones`**: Consultará la base de datos `nexus_memory.db` para listar los `thread_id` activos.
- **Nuevo Endpoint `/cargar_sesion`**: Permitirá recuperar el estado completo de una conversación pasada.

### [MODIFY] [index.html](file:///home/toloporto/proyectos/ecosistema_dev/index.html)
- Lógica de "Fetch" al cargar para rellenar el Sidebar.
- Evento `onClick` en los items del historial para cambiar el contexto de la conversación.

---

## Fase 6: Visión Multimodal Real (LLaVA)
**Objetivo:** Sustituir la simulación de radiografías por un análisis real de imagen.

### [MODIFY] [herramientas_nexus.py](file:///home/toloporto/proyectos/ecosistema_dev/herramientas_nexus.py)
- La herramienta `herramienta_vision_xray` dejará de devolver un número aleatorio.
- Se integrará una llamada a `Ollama` usando el modelo `llava` para analizar la imagen subida y describir hallazgos reales.

## Plan de Verificación
1. **Verificación Seguros:** Comprobar que tras un diagnóstico médico, Nexus informa sobre la cobertura del seguro.
2. **Verificación Historial:** Reiniciar el navegador y verificar que la consulta anterior aparece en la barra lateral y se puede recuperar.
3. **Verificación Visión:** Subir una imagen que no sea una radiografía y comprobar si LLaVA detecta que el contenido es incorrecto o describe lo que ve.
