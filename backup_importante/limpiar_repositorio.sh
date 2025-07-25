#!/bin/bash

# Script para limpiar completamente el repositorio
# y crear uno nuevo sin archivos grandes

set -e

echo "🧹 LIMPIADOR DE REPOSITORIO"
echo "============================"

# Verificar si estamos en el directorio correcto
if [[ ! -f "main.py" ]]; then
    echo "❌ No se encontró main.py. Asegúrate de estar en el directorio correcto."
    exit 1
fi

echo "📁 Creando backup de archivos importantes..."
mkdir -p backup_importante

# Copiar archivos importantes
cp main.py backup_importante/
cp principal.py backup_importante/
cp requirements.txt backup_importante/
cp *.py backup_importante/ 2>/dev/null || true
cp *.md backup_importante/ 2>/dev/null || true
cp *.sh backup_importante/ 2>/dev/null || true
cp *.bat backup_importante/ 2>/dev/null || true
cp *.ps1 backup_importante/ 2>/dev/null || true
cp -r assets backup_importante/ 2>/dev/null || true
cp *.db backup_importante/ 2>/dev/null || true

echo "✅ Backup creado en backup_importante/"

echo "🗑️ Eliminando directorios grandes..."
rm -rf dist/
rm -rf build/
rm -rf __pycache__/
rm -rf .git/

echo "✅ Directorios grandes eliminados"

echo "🔄 Inicializando nuevo repositorio Git..."
git init
git config user.name "Abdielcoder"
git config user.email "redskullcoder@gmail.com"

echo "📝 Agregando archivos al nuevo repositorio..."
git add .

echo "💾 Haciendo commit inicial..."
git commit -m "Initial commit - Herramientas Bonos"

echo "🔗 Configurando remote..."
git remote add origin git@github.com:Abdielcoder/int-bonos.git

echo "✅ Repositorio limpio creado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Verifica que todo esté correcto: git status"
echo "2. Haz push al repositorio: git push -u origin main"
echo "3. Si hay problemas, puedes restaurar desde backup_importante/" 