# src/utils/persistencia.py - Versión ajustada para usar 'datos/'
import json
import os
from datetime import datetime
from models.paciente import Paciente

def guardar_pacientes(pacientes_lista, archivo="datos/pacientes.json"):
    """Guarda la lista de pacientes en un archivo JSON"""
    try:
        # Crear directorio datos si no existe
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        
        # Convertir objetos Paciente a diccionarios
        datos = []
        for paciente in pacientes_lista:
            datos.append({
                "id": paciente.id,
                "nombre": paciente.nombre,
                "edad": paciente.edad,
                "sintomas": paciente.sintomas,
                "urgencia": paciente.urgencia,
                "fecha_registro": paciente.fecha_registro.isoformat()
            })
        
        # Guardar archivo
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Datos guardados en {archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False

def cargar_pacientes(archivo="datos/pacientes.json"):
    """Carga la lista de pacientes desde un archivo JSON"""
    try:
        if not os.path.exists(archivo):
            print(f"📂 No se encontró archivo previo en {archivo}")
            return []
        
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        # Reconstruir objetos Paciente
        pacientes = []
        for item in datos:
            paciente = Paciente(
                id=item["id"],
                nombre=item["nombre"],
                edad=item["edad"],
                sintomas=item["sintomas"],
                urgencia=item["urgencia"],
                fecha_registro=datetime.fromisoformat(item["fecha_registro"])
            )
            pacientes.append(paciente)
        
        print(f"📂 Cargados {len(pacientes)} paciente(s) desde {archivo}")
        return pacientes
    except Exception as e:
        print(f"❌ Error al cargar: {e}")
        return []

def exportar_estadisticas_txt(pacientes_lista, archivo="datos/estadisticas.txt"):
    """Exporta estadísticas a archivo de texto"""
    from collections import Counter
    
    try:
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("ESTADÍSTICAS DEL SISTEMA DE TRIAGE\n")
            f.write("="*50 + "\n\n")
            
            total = len(pacientes_lista)
            f.write(f"Total de pacientes: {total}\n\n")
            
            if total > 0:
                # Distribución por urgencia
                urgencias = {}
                for p in pacientes_lista:
                    nivel = p.urgencia.split(" - ")[0] if " - " in p.urgencia else p.urgencia[:10]
                    urgencias[nivel] = urgencias.get(nivel, 0) + 1
                
                f.write("Distribución por urgencia:\n")
                for nivel, count in urgencias.items():
                    f.write(f"  {nivel}: {count} paciente(s)\n")
                
                # Edades
                edades = [p.edad for p in pacientes_lista]
                f.write(f"\nEdad promedio: {sum(edades)/len(edades):.1f} años\n")
                f.write(f"Paciente más joven: {min(edades)} años\n")
                f.write(f"Paciente más adulto: {max(edades)} años\n")
                
                # Síntomas comunes
                todos_sintomas = []
                for p in pacientes_lista:
                    todos_sintomas.extend(p.sintomas)
                
                if todos_sintomas:
                    sintomas_comunes = Counter(todos_sintomas).most_common(5)
                    f.write("\nSíntomas más frecuentes:\n")
                    for sintoma, count in sintomas_comunes:
                        f.write(f"  {sintoma}: {count} caso(s)\n")
            
            f.write(f"\nExportado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        print(f"✅ Estadísticas exportadas a {archivo}")
        return True
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        return False

def ver_ultima_copia_seguridad():
    """Muestra información del último backup"""
    archivo = "datos/pacientes.json"
    if os.path.exists(archivo):
        tamaño = os.path.getsize(archivo)
        modificado = datetime.fromtimestamp(os.path.getmtime(archivo))
        print(f"\n📁 Información del archivo de datos:")
        print(f"  • Ubicación: {archivo}")
        print(f"  • Tamaño: {tamaño} bytes")
        print(f"  • Última modificación: {modificado.strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        print(f"\n📁 No existe archivo de datos en {archivo}")