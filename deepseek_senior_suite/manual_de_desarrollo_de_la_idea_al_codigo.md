Fase 1: El Despegue (Preparación del Entorno)
Nunca programes "suelto" en la carpeta personal. Dale a cada proyecto su propia casa.

1. Crear el territorio:

mkdir -p ~/proyectos/nombre_proyecto && cd $_



2. Activar el escudo (Entorno Virtual): Esto evita que las librerías de un proyecto rompan otro.

python3 -m venv .venv
source .venv/bin/activate

3. Llamar al editor:

code .


Fase 2: El Ciclo de Construcción (Iteración IA)

Aquí es donde aprovechas que tienes "becarios senior" viviendo en tu terminal.
. ESCRIBE: Crea tu archivo (ej. app.py) y escribe tu lógica inicial.
. REVISA: Antes de ejecutar, pide una segunda opinión técnica:

revisar_ia app.py

Tip: Usa Llama 3 (tu comando revisar_ia) para lógica y errores generales.
Si te atascas con una función muy compleja, usa DeepSeek directamente.

. CORRIGE: Aplica los cambios que tengan sentido. Recuerda: tú eres el jefe, la IA solo sugiere.


Fase 3: Ejecución y Pruebas

Una vez el código está limpio, es hora de la verdad.

1. Lanzar el programa:
python3 app.py

2. Gestionar librerías: Si instalas algo nuevo (como requests o pandas), regístralo siempre:
pip install nombre_libreria
pip freeze > requirements.txt

Fase 4: Mantenimiento y Cierre

Para que el "Antolín del futuro" no se vuelva loco cuando retome el proyecto dentro de un mes.

. Guardar progreso (Git):
git add .
git commit -m "Explicación breve de lo que has hecho hoy"

. Limpieza al salir:
deactivate

💡 Reglas de Oro del Programador con IA Local
. Regla del 80/20: La IA hará el 80% del trabajo pesado, 
pero tú eres responsable del 20% crítico (verificar que no "alucine").
. Privacidad: Recuerda que con Ollama, nada de lo que escribes sale de tu ordenador. 
Siéntete libre de usar datos reales o claves de prueba.
. Orden: Si un archivo empieza a ser muy largo (más de 200 líneas), 
divídelo en archivos más pequeños. Llama 3 te ayudará mejor con piezas pequeñas.
