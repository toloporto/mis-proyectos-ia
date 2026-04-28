# src/tools/buscador.py
from models.paciente import Paciente

def buscar_paciente(pacientes_lista, termino):
    """Busca pacientes por nombre o ID"""
    termino = termino.lower()
    resultados = []
    
    for paciente in pacientes_lista:
        if termino in paciente.nombre.lower() or termino in paciente.id.lower():
            resultados.append(paciente)
    
    return resultados

def mostrar_resultados_busqueda(resultados):
    """Muestra los resultados de búsqueda de forma bonita"""
    if not resultados:
        print("\n❌ No se encontraron pacientes.")
        return False
    
    print(f"\n🔍 Resultados encontrados: {len(resultados)}")
    print("-" * 40)
    
    for i, paciente in enumerate(resultados, 1):
        print(f"\n{i}. {paciente.nombre} (ID: {paciente.id})")
        print(f"   📍 Edad: {paciente.edad} años")
        print(f"   🤒 Síntomas: {', '.join(paciente.sintomas)}")
        print(f"   ⚠️  Urgencia: {paciente.urgencia}")
        # Dentro de mostrar_resultados_busqueda, después de print urgencia:
        print(f"   📅 Registrado: {paciente.fecha_registro.strftime('%d/%m/%Y %H:%M')}")
    
    return True
