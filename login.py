import hashlib

# En un sistema real, esto vendría de una base de datos
# Esta es la versión hash de "12345"
DB_USER = "admin"
DB_HASH = "5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5"

def validar_usuario(usuario, clave):
    """
    Compara el hash de la clave introducida con el almacenado.
    """
    # Convertimos la clave introducida a su representación SHA-256
    hash_input = hashlib.sha256(clave.encode()).hexdigest()
    
    # Retornamos directamente el resultado de la comparación (más limpio)
    return usuario == DB_USER and hash_input == DB_HASH

# --- Ejecución del programa ---
user_input = input("Usuario: ")
pass_input = input("Clave: ")

if validar_usuario(user_input, pass_input):
    print("✅ Acceso autorizado. ¡Bienvenido al sistema!")
else:
    print("❌ Error: Credenciales incorrectas.")