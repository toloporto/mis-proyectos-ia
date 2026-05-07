import csv
import random

def generar_medico(num_filas=2000):
    with open('dataset_medico.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['edad', 'presion', 'dolor', 'riesgo'])
        for _ in range(num_filas):
            edad = random.randint(18, 90)
            presion = random.randint(90, 180)
            dolor = random.randint(1, 10)
            
            # Lógica realista de riesgo
            riesgo = 0
            if (edad > 60 and presion > 140) or (dolor > 8):
                riesgo = 1
            if presion > 160:
                riesgo = 1
            
            # Un poco de ruido (5%) para que el modelo de ML aprenda patrones generales
            if random.random() < 0.05:
                riesgo = 1 - riesgo
                
            writer.writerow([edad, presion, dolor, riesgo])

def generar_financiero(num_filas=2000):
    with open('dataset_financiero.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ingresos', 'deuda', 'edad', 'riesgo'])
        for _ in range(num_filas):
            ingresos = random.randint(15, 120)
            deuda = random.randint(0, 80)
            edad = random.randint(18, 70)
            
            # Lógica realista de riesgo financiero
            riesgo = 0
            if deuda > (ingresos * 0.4): # Deuda mayor al 40% de ingresos
                riesgo = 1
            if edad < 25 and deuda > (ingresos * 0.2):
                riesgo = 1
                
            # Ruido (5%)
            if random.random() < 0.05:
                riesgo = 1 - riesgo
                
            writer.writerow([ingresos, deuda, edad, riesgo])

if __name__ == '__main__':
    print("--- FÁBRICA DE DATOS DEL ECOSISTEMA ---")
    print("Generando dataset_medico.csv (2000 historiales clínicos)...")
    generar_medico()
    print("Generando dataset_financiero.csv (2000 expedientes crediticios)...")
    generar_financiero()
    print("✅ Datasets creados con éxito. Listos para entrenar a los Agentes.")
