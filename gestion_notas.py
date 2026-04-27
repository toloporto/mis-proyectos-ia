# Un pequeño script para guardar notas en un archivo
def GuardarNota(texto):
    f = open("notas.txt", "a")
    f.write(texto + "\n")
    f.close()

miNota = "Aprender Linux es genial"
GuardarNota(miNota)
print("Nota guardada correctamente")