#!/bin/bash
# Script de ayuda para abrir bonosAlfa sin problemas de seguridad

echo "🔓 Abriendo bonosAlfa sin restricciones de seguridad..."

APP_PATH="dist/bonosAlfa.app"
if [[ -d "$APP_PATH" ]]; then
    echo "📱 Removiendo restricciones de quarantine..."
    xattr -d com.apple.quarantine "$APP_PATH" 2>/dev/null || echo "   (Sin restricciones previas)"
    
    echo "🚀 Abriendo bonosAlfa..."
    open "$APP_PATH"
    
    echo "✅ bonosAlfa se está abriendo..."
    echo "💡 Si sigue sin funcionar, ejecuta en Terminal:"
    echo "   sudo spctl --master-disable"
    echo "   (Esto desactiva Gatekeeper temporalmente)"
else
    echo "❌ No se encontró $APP_PATH"
    echo "💡 Asegúrate de ejecutar este script desde la carpeta del proyecto"
fi
