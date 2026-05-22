# Un pequeño script para guardar notas en un archivo
def GuardarNota(texto):
    with open("notas.txt", "a", encoding="utf-8") as f:
        f.write(texto + "\n")

miNota = "Aprender Linux es genial"
GuardarNota(miNota)
print("Nota guardada correctamente")