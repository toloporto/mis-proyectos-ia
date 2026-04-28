import os
import shutil

folder_path = '/home/toloporto/proyectos/multiagente/archivos_desordenados'

files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

extensions_count = {}
subfolder_paths = {}

# Contar extensiones
for file in files:
    file_path = os.path.join(folder_path, file)
    extension = os.path.splitext(file)[1]
    if extension not in extensions_count:
        extensions_count[extension] = 0
    extensions_count[extension] += 1

# Crear carpetas visibles (sin el punto)
for extension, count in extensions_count.items():
    subfolder_path = os.path.join(folder_path, extension.lstrip('.'))
    shutil.rmtree(subfolder_path, ignore_errors=True)
    if not os.path.isdir(subfolder_path):
        os.makedirs(subfolder_path)

# Mover archivos
for file in files:
    file_path = os.path.join(folder_path, file)
    extension = os.path.splitext(file)[1]
    subfolder_path = os.path.join(folder_path, extension.lstrip('.'))
    shutil.move(file_path, subfolder_path)

print("✅ ¡Archivos organizados en carpetas visibles por extensión!")