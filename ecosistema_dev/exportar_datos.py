import sqlite3
import json
import csv
import os

DB_NAME = "historial_medico.db"

def exportar_a_json():
    if not os.path.exists(DB_NAME):
        print(f"Error: La base de datos '{DB_NAME}' no existe.")
        return

    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    try:
        cursor.execute("SELECT * FROM historial")
        filas = cursor.fetchall()
        
        datos = [dict(fila) for fila in filas]
        
        with open('historial_exportado.json', 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
            
        print(f"✅ Se han exportado {len(datos)} registros a 'historial_exportado.json'.")
    except sqlite3.OperationalError as e:
        print(f"Error al leer la base de datos: {e}")
    finally:
        conexion.close()

def exportar_a_csv():
    if not os.path.exists(DB_NAME):
        print(f"Error: La base de datos '{DB_NAME}' no existe.")
        return

    conexion = sqlite3.connect(DB_NAME)
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()
    
    try:
        cursor.execute("SELECT * FROM historial")
        filas = cursor.fetchall()
        
        if not filas:
            print("No hay datos para exportar a CSV.")
            return

        columnas = filas[0].keys()
        
        with open('historial_exportado.csv', 'w', newline='', encoding='utf-8') as f:
            escritor = csv.DictWriter(f, fieldnames=columnas)
            escritor.writeheader()
            for fila in filas:
                escritor.writerow(dict(fila))
                
        print(f"✅ Se han exportado {len(filas)} registros a 'historial_exportado.csv'.")
    except sqlite3.OperationalError as e:
        print(f"Error al leer la base de datos: {e}")
    finally:
        conexion.close()

if __name__ == "__main__":
    print("=== HERRAMIENTA DE EXPORTACIÓN DE HISTORIAL MÉDICO ===")
    print("1. Exportar a JSON")
    print("2. Exportar a CSV")
    print("3. Exportar a ambos formatos (JSON y CSV)")
    
    opcion = input("Elige una opción (1/2/3): ")
    
    if opcion == '1':
        exportar_a_json()
    elif opcion == '2':
        exportar_a_csv()
    elif opcion == '3':
        exportar_a_json()
        exportar_a_csv()
    else:
        print("Opción no válida. Saliendo del programa.")
