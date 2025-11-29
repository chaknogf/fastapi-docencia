#!/bin/bash

set -e

echo "=== Comprobando sistema operativo ==="

OS=""
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="fedora"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "Sistema operativo no soportado."
    exit 1
fi

echo "Sistema detectado: $OS"
echo ""

# ----------------------------------------------------
#  VERIFICAR O INSTALAR PYTHON 3.14
# ----------------------------------------------------
echo "=== Verificando Python 3.14 ==="

PYVERSION=$(python3.14 -V 2>/dev/null || true)

if [[ -z "$PYVERSION" ]]; then
    echo "Python 3.14 no está instalado. Procediendo a instalar..."

    if [[ "$OS" == "fedora" ]]; then
        sudo dnf install -y python3.14 python3.14-pip python3.14-devel || {
            echo "Python 3.14 no está disponible en los repos de Fedora."
            echo "Instalando vía pyenv..."

            curl https://pyenv.run | bash

            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init -)"
            eval "$(pyenv virtualenv-init -)"

            pyenv install 3.14.0
            pyenv global 3.14.0
        }

    elif [[ "$OS" == "macos" ]]; then
        brew install python@3.14 || {
            echo "Python 3.14 no disponible en Homebrew. Usando pyenv..."
            brew install pyenv

            export PATH="$HOME/.pyenv/bin:$PATH"
            eval "$(pyenv init -)"

            pyenv install 3.14.0
            pyenv global 3.14.0
        }

        # Ajustar PATH
        echo 'export PATH="/opt/homebrew/opt/python@3.14/bin:$PATH"' >> ~/.zshrc
        source ~/.zshrc
    fi
else
    echo "Python 3.14 ya está instalado: $PYVERSION"
fi

echo ""

# ----------------------------------------------------
#  REPARAR CERTIFICADOS SSL (solo si Python existe)
# ----------------------------------------------------
echo "=== Configurando certificados SSL para Python ==="

CERT_CMD="/Library/Frameworks/Python.framework/Versions/3.14/bin/Install Certificates.command"

if [[ "$OS" == "macos" && -f "$CERT_CMD" ]]; then
    "$CERT_CMD"
fi

if [[ -d "/Library/Frameworks/Python.framework/Versions/3.14/etc/openssl" ]]; then
    curl -s https://curl.se/ca/cacert.pem -o /tmp/cacert.pem
    sudo cp /tmp/cacert.pem /Library/Frameworks/Python.framework/Versions/3.14/etc/openssl/cert.pem

    export SSL_CERT_FILE="/Library/Frameworks/Python.framework/Versions/3.14/etc/openssl/cert.pem"
fi

echo ""

# ----------------------------------------------------
#  LIMPIEZA DE ENTORNOS VIEJOS
# ----------------------------------------------------
echo "=== Eliminando entornos anteriores ==="
rm -rf .env .venv __pycache__

echo ""

# ----------------------------------------------------
#  INSTALAR POETRY
# ----------------------------------------------------
echo "=== Instalando Poetry ==="
rm -f ~/.local/bin/poetry
rm -rf ~/.local/pipx/venvs/poetry

curl -sSL https://install.python-poetry.org | python3.14 -
export PATH="$HOME/.local/bin:$PATH"

echo ""

# ----------------------------------------------------
#  CREAR ENTORNO VIRTUAL
# ----------------------------------------------------
echo "=== Creando entorno virtual ==="
python3.14 -m venv .venv
source .venv/bin/activate

echo "Actualizando pip..."
pip install --upgrade pip

echo "=== Instalando dependencias ==="
pip install -r requirements.txt

echo ""
echo "=== Sistema listo, señor Chak ==="
echo "Puede iniciar su API con:"
echo "uvicorn app.main:app --reload"