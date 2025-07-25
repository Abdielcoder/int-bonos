#!/bin/bash

# Script mejorado para crear instalador DMG con PySide6 incluido
# Uso: ./setup_dmg_fixed.sh

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

# Verificar PySide6
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📦 Instalando PySide6..."
    pip3 install PySide6
fi

# Instalar PyInstaller si no está disponible
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Verificar si create-dmg está disponible
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

# Construir aplicación con PyInstaller con configuración específica para PySide6
echo "🏗️ Construyendo aplicación..."

# Crear archivo spec personalizado para mejor control
cat > "Admin Bonos.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'requests',
        'pandas',
        'jwt',
        'json',
        'pathlib',
        'datetime',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Admin Bonos',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Admin Bonos',
)

app = BUNDLE(
    coll,
    name='Admin Bonos.app',
    icon='$ICNS_PATH',
    bundle_identifier='com.rinorisk.adminbonos',
    version='$APP_VERSION',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Admin Bonos Document',
                'CFBundleTypeIconFile': 'app_icon.icns',
                'LSItemContentTypes': ['com.rinorisk.adminbonos.document'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)
EOF

# Ejecutar PyInstaller con el spec personalizado
python3 -m PyInstaller "Admin Bonos.spec" --clean --noconfirm

if [[ ! -d "dist/$APP_NAME.app" ]]; then
    echo "❌ Error: No se pudo crear la aplicación"
    exit 1
fi

echo "✅ Aplicación construida: dist/$APP_NAME.app"

# Probar la aplicación construida
echo "🧪 Probando aplicación construida..."
if timeout 3 "dist/$APP_NAME.app/Contents/MacOS/$APP_NAME" 2>&1 | grep -q "Error"; then
    echo "⚠️ La aplicación puede tener problemas"
else
    echo "✅ Aplicación parece funcionar correctamente"
fi

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
    
    # Calcular tamaño necesario (más espacio para PySide6)
    APP_SIZE=$(du -sm "dist/$APP_NAME.app" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 100))  # Más espacio para PySide6
    
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
    echo "✅ PySide6 incluido en el bundle"
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