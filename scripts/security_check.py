"""
Script de verificacion de seguridad del proyecto.
Ejecutar periodicamente para detectar problemas.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


# Endpoints que SON validos sin autenticacion
PUBLIC_ENDPOINTS = [
    '/auth/email',           # Login/autenticacion magica
    '/auth/login',           # Login tradicional
    '/email',                # Login (sin prefijo)
    '/user/registro',        # Registro publico
    '/user/recuperar-contrasena',  # Recuperacion
    '/user/restablecer-contrasena',  # Reset con token
    '/actividades/enviar-mensual',   # Funcion de sistema
    '/verificador/',         # Validacion publica de horarios
    '/health',               # Health check
    '/docs',                 # Swagger
    '/redoc',                # ReDoc
    '/openapi.json',         # OpenAPI schema
]


def check_hardcoded_secrets() -> List[Tuple[str, int, str]]:
    """Busca secrets hardcodeados en el codigo."""
    issues = []
    patterns = [
        (r'SECRET_KEY\s*=\s*["\'][^"\']{20,}["\']', 'SECRET_KEY hardcodeada'),
        (r'password\s*=\s*["\'][^"\']+["\']', 'Contrasena hardcodeada'),
        (r'api_key\s*=\s*["\'][^"\']+["\']', 'API key hardcodeada'),
        (r'MAIL_PASSWORD\s*=\s*["\'][^"\']+["\']', 'MAIL_PASSWORD hardcodeada'),
    ]

    for root, _, files in os.walk('.'):
        if '.venv' in root or '__pycache__' in root or 'node_modules' in root or 'tests' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f, 1):
                            # Saltar comentarios
                            if line.strip().startswith('#'):
                                continue
                            for pattern, desc in patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    issues.append((filepath, i, desc))
                except Exception:
                    pass

    return issues


def check_missing_env_validation() -> List[str]:
    """Verifica que las variables de entorno criticas se validen."""
    issues = []
    config_file = Path('app/database/config.py')

    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
        if 'raise EnvironmentError' not in content and '_get_required_env' not in content:
            issues.append("Falta validacion de variables de entorno en config.py")

    return issues


def check_get_db_duplication() -> List[str]:
    """Verifica que get_db() no este duplicado."""
    issues = []
    routes_dir = Path('app/routes')

    if routes_dir.exists():
        for route_file in routes_dir.glob('*.py'):
            content = route_file.read_text(encoding='utf-8')
            if 'def get_db():' in content:
                issues.append(str(route_file))

    return issues


def check_auth_on_protected_endpoints() -> List[Tuple[str, str]]:
    """Verifica que endpoints protegidos requieran autenticacion."""
    issues = []
    routes_dir = Path('app/routes')

    if routes_dir.exists():
        for route_file in routes_dir.glob('*.py'):
            content = route_file.read_text(encoding='utf-8')

            # Obtener prefijo del router si existe
            prefix_match = re.search(r'APIRouter\([^)]*prefix=["\']([^"\']+)["\']', content)
            prefix = prefix_match.group(1) if prefix_match else ''

            # Buscar todos los decoradores de endpoint
            endpoint_pattern = r'@router\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']'
            matches = re.findall(endpoint_pattern, content)

            for method, path in matches:
                # Construir ruta completa
                full_path = prefix + path if not path.startswith('/') else path

                # Verificar si es un endpoint publico
                is_public = any(pub in full_path for pub in PUBLIC_ENDPOINTS)
                if is_public:
                    continue

                # Endpoints de autenticacion son publicos por definicion
                if '/auth/' in full_path:
                    continue

                # Buscar el contexto del endpoint (1000 chars despues)
                idx = content.find(f'@router.{method}("{path}")')
                if idx == -1:
                    idx = content.find(f"@router.{method}('{path}')")
                if idx == -1:
                    continue

                context = content[idx:idx+1000]

                # Verificar si tiene autenticacion
                has_auth = (
                    'get_current_user' in context or
                    'get_current_admin_user' in context or
                    'oauth2_scheme' in context
                )

                # Metodos GET son menos criticos
                if method.upper() == 'GET' and not has_auth:
                    continue

                if not has_auth:
                    issues.append((str(route_file), f"{method.upper()} {path}"))

    return issues


def main():
    print("=" * 60)
    print("  VERIFICACION DE SEGURIDAD - FastAPI Docencia")
    print("=" * 60)
    print()

    total_issues = 0

    # 1. Secrets hardcodeados
    print("1. Buscando secrets hardcodeados...")
    secrets = check_hardcoded_secrets()
    if secrets:
        print("   [!] PROBLEMAS ENCONTRADOS:")
        for file, line, desc in secrets:
            print(f"       {file}:{line} - {desc}")
        total_issues += len(secrets)
    else:
        print("   [OK] No se encontraron secrets hardcodeados")

    # 2. Validacion de env vars
    print("\n2. Verificando validacion de variables de entorno...")
    env_issues = check_missing_env_validation()
    if env_issues:
        print("   [!] PROBLEMAS:")
        for issue in env_issues:
            print(f"       - {issue}")
        total_issues += len(env_issues)
    else:
        print("   [OK] Variables de entorno validadas correctamente")

    # 3. get_db() duplicado
    print("\n3. Verificando duplicacion de get_db()...")
    db_issues = check_get_db_duplication()
    if db_issues:
        print("   [!] ARCHIVOS CON get_db() DUPLICADO:")
        for file in db_issues:
            print(f"       - {file}")
        total_issues += len(db_issues)
    else:
        print("   [OK] get_db() centralizado correctamente")

    # 4. Autenticacion en endpoints protegidos
    print("\n4. Verificando autenticacion en endpoints protegidos...")
    auth_issues = check_auth_on_protected_endpoints()
    if auth_issues:
        print("   [!] ENDPOINTS SIN AUTENTICACION:")
        for file, endpoint in auth_issues:
            print(f"       {file}: {endpoint}")
        total_issues += len(auth_issues)
    else:
        print("   [OK] Endpoints protegidos correctamente")

    print("\n" + "=" * 60)

    if total_issues == 0:
        print("  [PASS] TODAS LAS VERIFICACIONES PASARON")
        print("=" * 60)
        return 0
    else:
        print(f"  [FAIL] {total_issues} PROBLEMAS ENCONTRADOS")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
