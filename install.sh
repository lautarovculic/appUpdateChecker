#!/bin/bash

# Nombre del archivo destino
SCRIPT_NAME="appUpdateChecker"

# Ruta donde se instalará
INSTALL_PATH="/usr/local/bin/$SCRIPT_NAME"

echo "Installing $SCRIPT_NAME..."

# Descargar el script principal desde el repositorio de GitHub
curl -sSL "https://raw.githubusercontent.com/lautarovculic/appUpdateChecker/main/appUpdateChecker.py" -o "$INSTALL_PATH"

# Dar permisos de ejecución
chmod +x "$INSTALL_PATH"

echo "$SCRIPT_NAME installed successfully in $INSTALL_PATH"
echo "You can run the command '$SCRIPT_NAME'"
