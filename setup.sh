#!/bin/bash

# Check if uv is installed
if command -v uv &> /dev/null
then
    echo "✓ uv is already installed"
    uv --version
else
    echo "✗ uv is not installed"
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Check if installation was successful
    if [ $? -eq 0 ]; then
        echo "✓ uv has been successfully installed"
        echo "Please restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
    else
        echo "✗ Failed to install uv"
        exit 1
    fi
fi

