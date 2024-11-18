#!/bin/bash

# File name
SCRIPT_NAME="appUpdateChecker"

# Path install
INSTALL_PATH="$HOME/.local/bin/$SCRIPT_NAME"

echo "Installing $SCRIPT_NAME..."

# Download script
curl -sSL "https://raw.githubusercontent.com/lautarovculic/appUpdateChecker/main/appUpdateChecker.py" -o "$INSTALL_PATH"

# Execution permissions
chmod +x "$INSTALL_PATH"

echo "$SCRIPT_NAME installed successfully in $INSTALL_PATH"
echo "You can run the command '$SCRIPT_NAME'"
