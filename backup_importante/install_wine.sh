#!/bin/bash

# Script para instalar Wine en macOS
# Facilita la generación de ejecutables de Windows desde macOS

set -e

echo "🍷 INSTALADOR DE WINE PARA macOS"
echo "================================"

# Verificar si Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew no está instalado"
    echo "📦 Instalando Homebrew..."
    
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Agregar Homebrew al PATH
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    echo "✅ Homebrew instalado"
else
    echo "✅ Homebrew ya está instalado"
fi

# Verificar si Wine ya está instalado
if command -v wine &> /dev/null; then
    echo "✅ Wine ya está instalado"
    wine --version
else
    echo "🍷 Instalando Wine..."
    
    # Instalar Wine
    brew install --cask wine-stable
    
    echo "✅ Wine instalado"
fi

# Verificar si Rosetta 2 está instalado (necesario para Wine en Apple Silicon)
if [[ $(uname -m) == "arm64" ]]; then
    echo "🍎 Detectado Apple Silicon (M1/M2/M3)"
    
    if /usr/bin/pgrep -q oahd; then
        echo "✅ Rosetta 2 ya está instalado"
    else
        echo "📦 Instalando Rosetta 2..."
        softwareupdate --install-rosetta --agree-to-license
        echo "✅ Rosetta 2 instalado"
    fi
else
    echo "💻 Detectado Intel Mac"
fi

# Verificar la instalación
echo "🔍 Verificando instalación..."
if wine --version &> /dev/null; then
    echo "✅ Wine está funcionando correctamente"
    echo "🎉 ¡Instalación completada exitosamente!"
    echo ""
    echo "📋 Ahora puedes generar ejecutables de Windows:"
    echo "   python3 build_windows_wine.py"
else
    echo "❌ Wine no está funcionando correctamente"
    echo "   Intenta reiniciar la terminal y ejecutar:"
    echo "   wine --version"
    exit 1
fi 