#!/bin/bash

# Script para crear instalador DMG para Admin Bonos
# Uso: ./setup_dmg.sh

set -e  # Salir si hay algún error

# Configuración
APP_NAME="Admin Bonos"
APP_VERSION="1.0.0"
DMG_NAME="AdminBonos-${APP_VERSION}-macOS"
ICON_PATH="assets/img/logo.png"

echo "🚀 Iniciando creación de instalador DMG para $APP_NAME"
echo "📱 Versión: $APP_VERSION"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Verificar dependencias
echo "🔍 Verificando dependencias..."

# Verificar Python y pip
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Instalar PyInstaller si no está disponible
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Verificar si create-dmg está disponible (opcional)
if command -v create-dmg &> /dev/null; then
    echo "✅ create-dmg disponible"
    USE_CREATE_DMG=true
else
    echo "⚠️ create-dmg no disponible. Instalar con: brew install create-dmg"
    USE_CREATE_DMG=false
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec

# Convertir icono PNG a ICNS para macOS
echo "🎨 Convirtiendo icono..."
if [[ -f "$ICON_PATH" ]]; then
    ICONSET_PATH="assets/img/logo.iconset"
    ICNS_PATH="assets/img/logo.icns"
    
    # Crear directorio iconset
    mkdir -p "$ICONSET_PATH"
    
    # Generar diferentes tamaños
    for size in 16 32 64 128 256 512 1024; do
        echo "  Generando icono ${size}x${size}..."
        sips -z $size $size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}.png" > /dev/null 2>&1
        
        # Versiones @2x para retina (hasta 512)
        if [[ $size -le 512 ]]; then
            double_size=$((size * 2))
            sips -z $double_size $double_size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}@2x.png" > /dev/null 2>&1
        fi
    done
    
    # Convertir a ICNS
    iconutil -c icns "$ICONSET_PATH" -o "$ICNS_PATH"
    rm -rf "$ICONSET_PATH"
    
    ICON_FLAG="--icon $ICNS_PATH"
    echo "✅ Icono convertido"
else
    echo "⚠️ No se encontró el icono en $ICON_PATH"
    ICON_FLAG=""
fi

# Construir aplicación con PyInstaller
echo "🏗️ Construyendo aplicación..."
python3 -m PyInstaller \
    --onedir \
    --windowed \
    --noconfirm \
    --clean \
    --name "$APP_NAME" \
    --osx-bundle-identifier "com.rinorisk.adminbonos" \
    $ICON_FLAG \
    --add-data "assets:assets" \
    --add-data "requirements.txt:." \
    main.py

if [[ ! -d "dist/$APP_NAME.app" ]]; then
    echo "❌ Error: No se pudo crear la aplicación"
    exit 1
fi

echo "✅ Aplicación construida: dist/$APP_NAME.app"

# Crear DMG
echo "📦 Creando DMG..."

if [[ "$USE_CREATE_DMG" == true ]]; then
    # Método avanzado con create-dmg
    echo "🎨 Usando create-dmg para diseño avanzado..."
    
    create-dmg \
        --volname "$APP_NAME" \
        --volicon "$ICON_PATH" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 175 190 \
        --hide-extension "$APP_NAME.app" \
        --app-drop-link 425 190 \
        --no-internet-enable \
        "dist/$DMG_NAME.dmg" \
        "dist/$APP_NAME.app"
else
    # Método simple con hdiutil
    echo "🔧 Usando hdiutil para DMG básico..."
    
    # Calcular tamaño necesario
    APP_SIZE=$(du -sm "dist/$APP_NAME.app" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 50))
    
    # Crear DMG temporal
    TEMP_DMG="dist/temp_$DMG_NAME.dmg"
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_NAME" "$TEMP_DMG"
    
    # Montar DMG
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    # Copiar aplicación
    cp -R "dist/$APP_NAME.app" "$MOUNT_POINT/"
    
    # Crear enlace a Applications
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    # Desmontar
    hdiutil unmount "$MOUNT_POINT"
    
    # Convertir a DMG comprimido
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Verificar resultado
if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo ""
    echo "🎉 ¡Instalador DMG creado exitosamente!"
    echo "📦 Archivo: dist/$DMG_NAME.dmg"
    echo "💾 Tamaño: $DMG_SIZE"
    echo "📁 Aplicación: dist/$APP_NAME.app"
    echo ""
    echo "Para instalar:"
    echo "1. Abre el archivo DMG"
    echo "2. Arrastra '$APP_NAME.app' a la carpeta Applications"
    echo "3. Ejecuta la aplicación desde Applications"
else
    echo "❌ Error: No se pudo crear el DMG"
    exit 1
fi

# Limpiar archivos temporales
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec
if [[ -f "assets/img/logo.icns" ]]; then
    rm "assets/img/logo.icns"
fi

echo "✅ Proceso completado" 