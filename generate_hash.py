# generate_hash.py
"""
Script para generar hashes de contraseñas con Argon2.
Uso: python generate_hash.py
"""

from getpass import getpass
from app.database.security import pwd_context


def main():
    print("=" * 50)
    print("  Generador de Hash de Contraseñas")
    print("  Algoritmo: Argon2")
    print("=" * 50)
    print()

    password = getpass("Ingresa la contraseña a hashear: ")

    if not password:
        print("Error: La contraseña no puede estar vacía")
        return

    confirm = getpass("Confirma la contraseña: ")

    if password != confirm:
        print("Error: Las contraseñas no coinciden")
        return

    hash_result = pwd_context.hash(password)

    print()
    print("Hash generado exitosamente:")
    print("-" * 50)
    print(hash_result)
    print("-" * 50)
    print()
    print("Copia este hash para usarlo en la base de datos.")


if __name__ == "__main__":
    main()
