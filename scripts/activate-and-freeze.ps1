<# 
.SYNOPSIS
    Script de activación del entorno virtual con auto-actualización de requirements.txt

.DESCRIPTION
    Este script activa el entorno virtual del proyecto y actualiza automáticamente
    el archivo requirements.txt con las dependencias instaladas.

.NOTES
    Ejecutar: .\Scripts\activate-and-freeze.ps1
#>

# Colores para mensajes
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

Write-Host "${Green}========================================${Reset}"
Write-Host "${Green}  FastAPI Docencia - Activación Venv   ${Reset}"
Write-Host "${Green}========================================${Reset}"
Write-Host ""

# Verificar si estamos en la carpeta correcta
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "${Red}Error: No se encontró pyproject.toml${Reset}"
    Write-Host "Ejecuta este script desde la raíz del proyecto."
    exit 1
}

# Verificar si existe el entorno virtual
$venvPath = ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "${Yellow}Creando entorno virtual...${Reset}"
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "${Red}Error al crear el entorno virtual${Reset}"
        exit 1
    }
}

# Activar entorno virtual
Write-Host "${Yellow}Activando entorno virtual...${Reset}"
& "$venvPath\Scripts\Activate.ps1"

# Verificar si poetry está instalado
if (Get-Command "poetry" -ErrorAction SilentlyContinue) {
    Write-Host "${Yellow}Instalando dependencias con Poetry...${Reset}"
    poetry install
} else {
    Write-Host "${Yellow}Poetry no encontrado. Usando pip...${Reset}"
    
    if (Test-Path "requirements.txt") {
        Write-Host "${Yellow}Instalando desde requirements.txt...${Reset}"
        pip install -r requirements.txt
    } else {
        Write-Host "${Yellow}requirements.txt no encontrado. Instalando dependencias principales...${Reset}"
        pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose passlib argon2-cffi fastapi-mail python-dotenv openpyxl apscheduler
    }
}

# Actualizar requirements.txt con pip freeze
Write-Host ""
Write-Host "${Yellow}Actualizando requirements.txt...${Reset}"
pip freeze > requirements.txt
Write-Host "${Green}requirements.txt actualizado exitosamente${Reset}"

# Verificar .env
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "${Yellow}Archivo .env no encontrado.${Reset}"
    Write-Host "Copia .env.example como .env y completa las variables:"
    Write-Host "  copy .env.example .env"
}

Write-Host ""
Write-Host "${Green}========================================${Reset}"
Write-Host "${Green}  Entorno listo para desarrollo         ${Reset}"
Write-Host "${Green}========================================${Reset}"
Write-Host ""
Write-Host "Ejecutar servidor:"
Write-Host "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
Write-Host ""
