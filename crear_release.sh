#!/bin/bash

# Script para crear releases de Herramientas Bonos
# Uso: ./crear_release.sh [version]
# Ejemplo: ./crear_release.sh 1.0.0

set -e

# Obtener versión del argumento o generar automáticamente
if [ -z "$1" ]; then
    # Generar versión automática basada en fecha
    VERSION=$(date +"%Y.%m.%d")
    echo "No se especificó versión, usando: $VERSION"
else
    VERSION="$1"
fi

echo "🚀 Creando release v$VERSION..."

# Verificar que estamos en el branch main
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Debes estar en el branch main para crear releases"
    echo "   Branch actual: $CURRENT_BRANCH"
    exit 1
fi

# Verificar que no hay cambios pendientes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Hay cambios pendientes. Haz commit antes de crear el release"
    git status --short
    exit 1
fi

# Crear tag
echo "📝 Creando tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push del tag
echo "📤 Subiendo tag a GitHub..."
git push origin "v$VERSION"

echo "✅ Release v$VERSION creado exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. El workflow de GitHub Actions se ejecutará automáticamente"
echo "   2. Se compilará el ejecutable de Windows"
echo "   3. Se creará el release en GitHub con el ejecutable"
echo ""
echo "🔗 Puedes ver el progreso en:"
echo "   https://github.com/Abdielcoder/int-bonos/actions"
echo ""
echo "📦 El release estará disponible en:"
echo "   https://github.com/Abdielcoder/int-bonos/releases/tag/v$VERSION" 