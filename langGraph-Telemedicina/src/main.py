# src/main.py - Versión completa con todas las mejoras
import sys
import os
from collections import Counter

# Añadir la ruta del proyecto para poder importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar herramientas locales (no requieren API)
from tools.validador_sintomas import validar_sintomas, calcular_urgencia, obtener_recomendacion
from models.paciente import Paciente
from datetime import datetime
# Añade estas líneas después de los otros imports
from utils.persistencia import guardar_pacientes, cargar_pacientes, exportar_estadisticas_txt
from tools.buscador import buscar_paciente, mostrar_resultados_busqueda
# Después de los otros imports
from agents.sistema_multiagente import consultar_sistema_multiagente
from agents.sistema_multiagente_ollama import consultar_sistema_multiagente

# Lista temporal de pacientes (simula una base de datos)
pacientes_registrados = []

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*50)
    print("🏥 SISTEMA DE TRIAGE MÉDICO - LangGraph")
    print("="*50)
    print("1. 🔍 Validar síntomas (sin IA)")
    print("2. 📝 Registrar nuevo paciente")
    print("3. 📋 Ver pacientes registrados")
    print("4. ⚕️  Calcular urgencia manual")
    print("5. 📊 Ver estadísticas del sistema")
    print("6. 🚀 Probar integración con LangGraph (básico)")
    print("7. 🔎 Buscar paciente")
    print("8. 💾 Exportar estadísticas")
    print("9. 🤖 SISTEMA MULTIAGENTE LANGGRAPH (NUEVO)")
    print("0. ❌ Salir")
    print("="*50)

def opcion_validar_sintomas():
    """Opción 1: Validar síntomas localmente (versión mejorada)"""
    print("\n🔍 VALIDADOR DE SÍNTOMAS")
    consulta = input("Describe tus síntomas: ")
    
    # Usar la herramienta mejorada
    resultado = validar_sintomas(consulta)
    
    print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
    print("-" * 40)
    
    if resultado['sintomas_encontrados']:
        print(f"🤒 Síntomas detectados: {', '.join(resultado['sintomas_encontrados'])}")
        print(f"📊 Cantidad: {resultado['cantidad']} síntoma(s)")
        
        # Mostrar detalles adicionales
        if resultado['detalles']['tiene_dolor']:
            print("⚠️  Se detectó dolor - evaluar intensidad")
        if resultado['detalles']['tiene_fiebre']:
            print("🌡️  Se detectó fiebre - monitorear temperatura")
        if resultado['detalles']['tiene_dificultad_respiratoria']:
            print("🫁 ¡ATENCIÓN! Dificultad respiratoria detectada")
    else:
        print("❓ No se detectaron síntomas en el texto proporcionado")
        print("   Intenta ser más específico (ej: 'dolor de cabeza', 'fiebre', 'tos')")
    
    # Calcular urgencia
    urgencia = calcular_urgencia(resultado['sintomas_encontrados'])
    print(f"\n⚠️  NIVEL DE URGENCIA: {urgencia}")
    
    # Mostrar recomendación
    recomendacion = obtener_recomendacion(resultado['sintomas_encontrados'], urgencia)
    print(f"\n💡 RECOMENDACIÓN:\n   {recomendacion}")
    
    # Consejo adicional si no hay síntomas
    if resultado['cantidad'] == 0:
        print("\n💡 Consejo: Describe síntomas específicos como:")
        print("   • 'Me duele la cabeza y tengo fiebre'")
        print("   • 'Tengo dificultad para respirar'")
        print("   • 'Me duele el pecho'")

def opcion_registrar_paciente():
    """Opción 2: Registrar nuevo paciente (con manejo de errores)"""
    print("\n📝 REGISTRO DE PACIENTE")
    nombre = input("Nombre: ")
    
    # Manejo de error para la edad
    while True:
        try:
            edad = int(input("Edad: "))
            if edad < 0 or edad > 150:
                print("❌ Edad no válida. Debe estar entre 0 y 150 años.")
                continue
            break
        except ValueError:
            print("❌ Por favor, ingresa un número válido para la edad.")
    
    sintomas_texto = input("Síntomas (separados por comas): ")
    sintomas = [s.strip() for s in sintomas_texto.split(",") if s.strip()]
    
    # Validar que haya al menos un síntoma
    if not sintomas:
        print("⚠️  No se registraron síntomas. El paciente se guardará sin síntomas.")
    
    # Crear ID automático
    paciente_id = f"PAC-{len(pacientes_registrados)+1:04d}"
    
    # Calcular urgencia automáticamente
    urgencia = calcular_urgencia(sintomas)
    
    # Crear objeto paciente
    nuevo_paciente = Paciente(
        id=paciente_id,
        nombre=nombre,
        edad=edad,
        sintomas=sintomas,
        urgencia=urgencia,
        fecha_registro=datetime.now()
    )
    
    pacientes_registrados.append(nuevo_paciente)
    print(f"\n✅ Paciente registrado con ID: {paciente_id}")
    print(f"   Urgencia asignada: {urgencia}")
    
    # Mostrar recomendación basada en urgencia
    if "ROJO" in urgencia:
        print("   🚨 ¡ATENCIÓN! Este paciente requiere atención inmediata.")
    elif "AMARILLO" in urgencia:
        print("   ⚠️  Este paciente requiere atención prioritaria.")

def opcion_ver_pacientes():
    """Opción 3: Ver pacientes registrados"""
    print("\n📋 LISTA DE PACIENTES")
    if not pacientes_registrados:
        print("  No hay pacientes registrados aún.")
        return
    
    for i, paciente in enumerate(pacientes_registrados, 1):
        print(f"\n{i}. {paciente.nombre} (ID: {paciente.id})")
        print(f"   📍 Edad: {paciente.edad} años")
        print(f"   🤒 Síntomas: {', '.join(paciente.sintomas) if paciente.sintomas else 'Ninguno registrado'}")
        print(f"   ⚠️  Urgencia: {paciente.urgencia}")
        print(f"   📅 Registrado: {paciente.fecha_registro.strftime('%d/%m/%Y %H:%M')}")

def opcion_calcular_urgencia_manual():
    """Opción 4: Calcular urgencia manualmente (mejorada)"""
    print("\n⚕️  CALCULADORA DE URGENCIA")
    print("   (Usa palabras clave como: dolor, fiebre, tos, respiración, pecho)")
    
    sintomas_texto = input("Ingresa síntomas (separados por comas): ")
    sintomas = [s.strip().lower() for s in sintomas_texto.split(",") if s.strip()]
    
    if not sintomas:
        print("❌ No ingresaste ningún síntoma válido.")
        return
    
    # Usar la misma función mejorada que en opción 1
    urgencia = calcular_urgencia(sintomas)
    
    print(f"\n📊 RESULTADO DEL ANÁLISIS:")
    print("-" * 40)
    print(f"  • Síntomas evaluados: {', '.join(sintomas)}")
    print(f"  • Cantidad: {len(sintomas)} síntoma(s)")
    print(f"  • Nivel de urgencia: {urgencia}")
    
    # Mostrar recomendación
    recomendacion = obtener_recomendacion(sintomas, urgencia)
    print(f"\n💡 RECOMENDACIÓN:\n   {recomendacion}")
    
    # Detección adicional de palabras clave
    palabras_alta_prioridad = ["pecho", "respirar", "ahogo", "presión", "desmayo"]
    palabras_detectadas = [p for p in palabras_alta_prioridad if p in sintomas_texto.lower()]
    
    if palabras_detectadas:
        print(f"\n⚠️  ALERTA: Se detectaron palabras clave de alta prioridad: {', '.join(palabras_detectadas)}")

def opcion_estadisticas():
    """Opción 5: Mostrar estadísticas del sistema"""
    print("\n📊 ESTADÍSTICAS DEL SISTEMA")
    print("-" * 40)
    
    total_pacientes = len(pacientes_registrados)
    print(f"📋 Total de pacientes registrados: {total_pacientes}")
    
    if total_pacientes > 0:
        # Contar por nivel de urgencia
        urgencias = {
            "ROJO": 0,
            "AMARILLO": 0, 
            "VERDE": 0,
            "AZUL": 0,
            "BLANCO": 0
        }
        
        for paciente in pacientes_registrados:
            encontrado = False
            for nivel in urgencias.keys():
                if nivel in paciente.urgencia:
                    urgencias[nivel] += 1
                    encontrado = True
                    break
            if not encontrado:
                urgencias["BLANCO"] += 1
        
        print("\n📊 Distribución por urgencia:")
        for nivel, cantidad in urgencias.items():
            if cantidad > 0:
                emoji = "🔴" if nivel == "ROJO" else "🟡" if nivel == "AMARILLO" else "🟢" if nivel == "VERDE" else "🔵" if nivel == "AZUL" else "⚪"
                print(f"  {emoji} {nivel}: {cantidad} paciente(s)")
        
        # Edad promedio
        edades = [p.edad for p in pacientes_registrados]
        edad_promedio = sum(edades) / len(edades)
        print(f"\n📊 Edad promedio: {edad_promedio:.1f} años")
        print(f"  • Paciente más joven: {min(edades)} años")
        print(f"  • Paciente más adulto: {max(edades)} años")
        
        # Síntomas más comunes
        todos_sintomas = []
        for paciente in pacientes_registrados:
            todos_sintomas.extend(paciente.sintomas)
        
        if todos_sintomas:
            sintomas_comunes = Counter(todos_sintomas).most_common(3)
            print(f"\n🤒 Síntomas más frecuentes:")
            for sintoma, count in sintomas_comunes:
                print(f"  • {sintoma}: {count} caso(s)")
        else:
            print("\n🤒 No hay síntomas registrados para análisis.")
        
        # Pacientes por rango etario
        menores_18 = sum(1 for p in pacientes_registrados if p.edad < 18)
        adultos = sum(1 for p in pacientes_registrados if 18 <= p.edad < 65)
        mayores_65 = sum(1 for p in pacientes_registrados if p.edad >= 65)
        
        print(f"\n👥 Distribución por edad:")
        print(f"  • Menores de 18: {menores_18} paciente(s)")
        print(f"  • Adultos (18-64): {adultos} paciente(s)")
        print(f"  • Mayores de 65: {mayores_65} paciente(s)")
        
    else:
        print("  Aún no hay datos para mostrar estadísticas.")
        print("  Registra algunos pacientes usando la opción 2.")

def opcion_buscar_paciente():
    """Opción 7: Buscar paciente por nombre o ID"""
    print("\n🔎 BUSCAR PACIENTE")
    termino = input("Ingresa nombre o ID del paciente: ")
    
    resultados = buscar_paciente(pacientes_registrados, termino)
    mostrar_resultados_busqueda(resultados)

def opcion_exportar_estadisticas():
    """Opción 8: Exportar estadísticas a archivo"""
    print("\n📁 EXPORTAR ESTADÍSTICAS")
    
    if exportar_estadisticas_txt(pacientes_registrados):
        print("\n✅ Estadísticas exportadas exitosamente a 'data/estadisticas.txt'")
        print("   Puedes ver el archivo con: cat data/estadisticas.txt")
    else:
        print("\n❌ Error al exportar estadísticas.")

def opcion_multiagente_langgraph():
    """Opción 9: Sistema multiagente real con LangGraph"""
    print("\n" + "="*50)
    print("🤖 SISTEMA MULTIAGENTE LANGGRAPH")
    print("="*50)
    print("   Este sistema utiliza 3 agentes IA que trabajan en cadena:")
    print("   1. Agente TRIAGE - Clasifica la urgencia")
    print("   2. Agente DIAGNÓSTICO - Identifica condiciones")
    print("   3. Agente TRATAMIENTO - Recomienda acciones")
    print("="*50)
    
    consulta = input("\n🩺 Describe los síntomas del paciente: ")
    
    if not consulta.strip():
        print("❌ No ingresaste síntomas.")
        return
    
    # Verificar API key
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ ERROR: No tienes configurada la API key de OpenAI")
        print("   Crea un archivo .env con: OPENAI_API_KEY=tu_clave")
        return
    
    print("\n🔄 Ejecutando sistema multiagente...")
    print("   Los agentes están trabajando (esto puede tomar 10-15 segundos)...")
    
    try:
        resultado = consultar_sistema_multiagente(consulta)
        if resultado:
            print(f"\n💾 ¿Deseas guardar esta consulta en el historial del paciente?")
            guardar = input("¿Guardar? (s/n): ").lower()
            if guardar == 's':
                # Aquí podrías guardar el resultado en el sistema existente
                print("   (Funcionalidad de guardado en desarrollo)")
    except Exception as e:
        print(f"\n❌ Error al ejecutar el sistema multiagente: {e}")

def opcion_multiagente():
    """Opción 9: Sistema multiagente con Ollama (gratuito)"""
    print("\n" + "="*50)
    print("🤖 SISTEMA MULTIAGENTE LANGGRAPH")
    print("   Usando Ollama local (completamente GRATUITO)")
    print("   3 agentes IA trabajan en cadena")
    print("="*50)
    
    sintomas = input("\n🩺 Describe los síntomas del paciente: ")
    if sintomas.strip():
        consultar_sistema_multiagente(sintomas)
    else:
        print("❌ Síntomas no válidos")

def opcion_probar_langgraph():
    """Opción 6: Probar integración con LangGraph (requiere API key)"""
    print("\n🚀 PROBANDO INTEGRACIÓN CON LANGGRAPH")
    print("  Esta opción requiere OpenAI API key configurada en .env")
    
    # Verificar si existe API key
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "tu_clave_aqui":
        print("\n⚠️  No se encontró API key válida.")
        print("  Para usar esta función:")
        print("  1. Crea un archivo .env en la raíz del proyecto")
        print("  2. Añade: OPENAI_API_KEY=tu_clave_real")
        print("  3. Ejecuta: pip install langchain-openai python-dotenv")
        print("\n  Mientras tanto, puedes usar las opciones 1-5 que funcionan sin API.")
        return
    
    try:
        # Importar módulo de triage (requiere API)
        from agents.triage_agent import triage_app
        
        consulta = input("\nDescribe los síntomas del paciente: ")
        print("\n🤔 Analizando con IA... (esto puede tomar unos segundos)")
        
        resultado = triage_app.invoke({"messages": [("user", consulta)]})
        respuesta = resultado['messages'][-1].content
        
        print(f"\n📊 Resultado del triage con IA:")
        print(f"  {respuesta}")
        print("\n💡 La IA ha analizado los síntomas y generado una clasificación.")
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("  Asegúrate de tener instalado: pip install langgraph langchain-openai")
    except Exception as e:
        print(f"\n❌ Error al usar LangGraph: {e}")
        print("  Verifica que tu API key sea válida y tengas créditos disponibles.")

def main():
    """Función principal"""
    global pacientes_registrados
    
    # Cargar pacientes guardados anteriormente
    pacientes_registrados = cargar_pacientes()
    if pacientes_registrados:
        print(f"\n📂 Cargados {len(pacientes_registrados)} paciente(s) de la base de datos.")
    
    print("\n✨ ¡Bienvenido al Sistema de Triage Médico!")
    print("   Proyecto inicializado y listo para codificar")
    print("   Versión mejorada con estadísticas y manejo de errores")
    
    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            opcion_validar_sintomas()
        elif opcion == "2":
            opcion_registrar_paciente()
            # Guardar automáticamente después de registrar
            guardar_pacientes(pacientes_registrados)
        elif opcion == "3":
            opcion_ver_pacientes()
        elif opcion == "4":
            opcion_calcular_urgencia_manual()
        elif opcion == "5":
            opcion_estadisticas()
        elif opcion == "6":
            opcion_probar_langgraph()
        elif opcion == "7":  # Nueva opción de búsqueda
            opcion_buscar_paciente()
        elif opcion == "8":  # Nueva opción de exportar
            opcion_exportar_estadisticas()
        elif opcion == "9":
            opcion_multiagente()
        elif opcion == "0":
            # Guardar antes de salir
            guardar_pacientes(pacientes_registrados)
            print("\n👋 ¡Hasta luego! Gracias por usar el sistema.")
            print(f"   Total de pacientes atendidos: {len(pacientes_registrados)}")
            print(f"   Datos guardados en data/pacientes.json")
            break
        else:
            print("\n❌ Opción no válida. Intenta de nuevo.")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()