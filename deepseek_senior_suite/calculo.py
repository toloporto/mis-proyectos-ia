def dividir_numeros(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Error: División por cero no permitida"

num1 = 10
num2 = 0 # Esto daría un error, pero ahora está manejado
print(dividir_numeros(num1, num2))
