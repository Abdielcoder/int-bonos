#!/bin/bash

# Script para configurar Git para el usuario Abdielcoder
# Soluciona problemas de permisos y configuración

set -e

echo "🔧 CONFIGURADOR DE GIT PARA ABDIELCODER"
echo "======================================="

# Configurar usuario Git
echo "👤 Configurando usuario Git..."
git config --global user.name "Abdielcoder"
git config --global user.email "redskullcoder@gmail.com"

echo "✅ Usuario configurado:"
echo "   Nombre: $(git config --global user.name)"
echo "   Email: $(git config --global user.email)"

# Verificar si existe la nueva clave SSH
if [[ -f ~/.ssh/id_ed25519_abdielcoder ]]; then
    echo "🔑 Clave SSH encontrada para Abdielcoder"
    
    # Mostrar la clave pública
    echo "📋 Tu clave pública SSH es:"
    echo "----------------------------------------"
    cat ~/.ssh/id_ed25519_abdielcoder.pub
    echo "----------------------------------------"
    
    echo ""
    echo "📋 INSTRUCCIONES PARA GITHUB:"
    echo "1. Ve a https://github.com/settings/keys"
    echo "2. Haz clic en 'New SSH key'"
    echo "3. Title: MacBook Abdielcoder"
    echo "4. Key: Copia y pega la clave de arriba"
    echo "5. Haz clic en 'Add SSH key'"
    echo ""
    
    # Configurar SSH para usar la nueva clave
    echo "🔧 Configurando SSH..."
    if [[ ! -f ~/.ssh/config ]]; then
        touch ~/.ssh/config
        chmod 600 ~/.ssh/config
    fi
    
    # Agregar configuración para GitHub
    if ! grep -q "github.com" ~/.ssh/config; then
        echo "" >> ~/.ssh/config
        echo "# GitHub para Abdielcoder" >> ~/.ssh/config
        echo "Host github.com" >> ~/.ssh/config
        echo "  HostName github.com" >> ~/.ssh/config
        echo "  User git" >> ~/.ssh/config
        echo "  IdentityFile ~/.ssh/id_ed25519_abdielcoder" >> ~/.ssh/config
        echo "  IdentitiesOnly yes" >> ~/.ssh/config
    fi
    
    echo "✅ Configuración SSH completada"
    
    # Probar conexión SSH
    echo "🧪 Probando conexión SSH..."
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ Conexión SSH exitosa"
    else
        echo "⚠️ Conexión SSH falló - agrega la clave a GitHub primero"
    fi
    
else
    echo "❌ No se encontró la clave SSH para Abdielcoder"
    echo "   Ejecuta: ssh-keygen -t ed25519 -C 'redskullcoder@gmail.com' -f ~/.ssh/id_ed25519_abdielcoder"
fi

# Configurar el repositorio
echo "📁 Configurando repositorio..."
git remote set-url origin git@github.com:Abdielcoder/int-bonos.git

echo "✅ Repositorio configurado:"
git remote -v

echo ""
echo "🎉 Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Agrega la clave SSH a GitHub (si no lo has hecho)"
echo "2. Ejecuta: git push -u origin main"
echo "3. Para GitHub Actions: python3 setup_github_actions.py" 