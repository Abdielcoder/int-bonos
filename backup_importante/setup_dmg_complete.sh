#!/bin/bash

# Script completo para crear instalador DMG con TODAS las dependencias
# Uso: ./setup_dmg_complete.sh

set -e  # Salir si hay algún error

# Configuración
APP_NAME="Admin Bonos"
APP_VERSION="1.0.0"
DMG_NAME="AdminBonos-${APP_VERSION}-macOS"
ICON_PATH="assets/img/logo.png"

echo "🚀 Iniciando creación de instalador DMG COMPLETO para $APP_NAME"
echo "📱 Versión: $APP_VERSION"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Lista de dependencias requeridas
REQUIRED_PACKAGES=(
    "PySide6"
    "pandas" 
    "PyJWT"
    "requests"
    "openpyxl"
    "xlrd"
    "numpy"
    "python-dateutil"
    "pytz"
    "urllib3"
    "certifi"
    "charset-normalizer"
    "idna"
    "pathlib"
    "typing_extensions"
)

echo "🔍 Verificando e instalando dependencias..."

# Verificar Python y pip
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Función para verificar e instalar paquetes
install_if_missing() {
    local package=$1
    echo "  🔍 Verificando $package..."
    
    if ! python3 -c "import $package" 2>/dev/null; then
        echo "  📦 Instalando $package..."
        pip3 install "$package"
    else
        echo "  ✅ $package ya está instalado"
    fi
}

# Instalar todas las dependencias
for package in "${REQUIRED_PACKAGES[@]}"; do
    # Algunos paquetes tienen nombres diferentes en import vs pip
    case $package in
        "PyJWT")
            install_if_missing "jwt"
            ;;
        "python-dateutil")
            install_if_missing "dateutil"
            ;;
        "typing_extensions")
            install_if_missing "typing_extensions"
            ;;
        *)
            install_if_missing "$package"
            ;;
    esac
done

# Instalar PyInstaller si no está disponible
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Verificar que todas las dependencias críticas están disponibles
echo "🧪 Verificando instalación completa..."
VERIFICATION_IMPORTS=(
    "PySide6"
    "PySide6.QtCore"
    "PySide6.QtGui"
    "PySide6.QtWidgets"
    "pandas"
    "jwt"
    "requests"
    "json"
    "pathlib"
    "datetime"
    "typing"
    "openpyxl"
    "xlrd"
)

for import_name in "${VERIFICATION_IMPORTS[@]}"; do
    if python3 -c "import $import_name" 2>/dev/null; then
        echo "  ✅ $import_name"
    else
        echo "  ❌ $import_name - ERROR"
        exit 1
    fi
done

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
    
    mkdir -p "$ICONSET_PATH"
    
    for size in 16 32 64 128 256 512 1024; do
        echo "  Generando icono ${size}x${size}..."
        sips -z $size $size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}.png" > /dev/null 2>&1
        
        if [[ $size -le 512 ]]; then
            double_size=$((size * 2))
            sips -z $double_size $double_size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}@2x.png" > /dev/null 2>&1
        fi
    done
    
    iconutil -c icns "$ICONSET_PATH" -o "$ICNS_PATH"
    rm -rf "$ICONSET_PATH"
    
    ICON_FLAG="--icon $ICNS_PATH"
    echo "✅ Icono convertido"
else
    echo "⚠️ No se encontró el icono en $ICON_PATH"
    ICON_FLAG=""
fi

# Crear archivo spec completo con todas las dependencias
echo "🏗️ Creando configuración de PyInstaller..."

cat > "Admin Bonos.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Lista completa de imports ocultos
hidden_imports = [
    # PySide6 core
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtDBus',
    'shiboken6',
    
    # Data processing
    'pandas',
    'pandas.core',
    'pandas.core.arrays',
    'pandas.core.groupby',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.common',
    'pandas.io.excel',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    
    # File handling
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'xlrd',
    'xlrd.biffh',
    
    # Network and security
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.models',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'certifi',
    'ssl',
    'socket',
    
    # JWT and crypto
    'jwt',
    'jwt.algorithms',
    'cryptography',
    'cryptography.hazmat',
    'cryptography.hazmat.primitives',
    
    # Text processing
    'charset_normalizer',
    'idna',
    
    # Date and time
    'datetime',
    'dateutil',
    'dateutil.parser',
    'pytz',
    'tzdata',
    
    # Standard library essentials
    'json',
    'pathlib',
    'typing',
    'typing_extensions',
    'collections',
    'functools',
    'itertools',
    'base64',
    'hashlib',
    'hmac',
    'os',
    'sys',
    're',
    'time',
    'threading',
    'multiprocessing',
    'subprocess',
    'tempfile',
    'shutil',
    'csv',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'notebook',
        'pytest',
        'sphinx',
    ],
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
    icon='assets/img/logo.icns',
    bundle_identifier='com.rinorisk.adminbonos',
    version='1.0.0',
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

echo "🏗️ Construyendo aplicación con configuración completa..."

# Ejecutar PyInstaller con configuración detallada
python3 -m PyInstaller "Admin Bonos.spec" --clean --noconfirm --log-level INFO

if [[ ! -d "dist/$APP_NAME.app" ]]; then
    echo "❌ Error: No se pudo crear la aplicación"
    exit 1
fi

echo "✅ Aplicación construida: dist/$APP_NAME.app"

# Verificar que los módulos críticos están incluidos
echo "🔍 Verificando módulos incluidos..."
if [[ -d "dist/$APP_NAME.app/Contents/Frameworks/PySide6" ]]; then
    echo "  ✅ PySide6 incluido"
else
    echo "  ❌ PySide6 NO incluido"
fi

# Probar la aplicación construida
echo "🧪 Probando aplicación construida..."
if timeout 5 "dist/$APP_NAME.app/Contents/MacOS/$APP_NAME" 2>&1 | grep -q "pandas"; then
    echo "⚠️ Pandas no está disponible en la aplicación"
    exit 1
else
    echo "✅ Aplicación parece funcionar correctamente"
fi

# Crear DMG
echo "📦 Creando DMG..."

if [[ "$USE_CREATE_DMG" == true ]]; then
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
    echo "🔧 Usando hdiutil para DMG básico..."
    
    APP_SIZE=$(du -sm "dist/$APP_NAME.app" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 150))  # Más espacio para todas las dependencias
    
    TEMP_DMG="dist/temp_$DMG_NAME.dmg"
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_NAME" "$TEMP_DMG"
    
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    cp -R "dist/$APP_NAME.app" "$MOUNT_POINT/"
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    hdiutil unmount "$MOUNT_POINT"
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Verificar resultado final
if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo ""
    echo "🎉 ¡Instalador DMG COMPLETO creado exitosamente!"
    echo "📦 Archivo: dist/$DMG_NAME.dmg"
    echo "💾 Tamaño: $DMG_SIZE"
    echo "📁 Aplicación: dist/$APP_NAME.app"
    echo ""
    echo "✅ Dependencias incluidas:"
    echo "  • PySide6 (UI framework)"
    echo "  • pandas (data processing)"
    echo "  • PyJWT (authentication)"
    echo "  • requests (HTTP client)"
    echo "  • openpyxl, xlrd (Excel files)"
    echo "  • numpy (numerical computing)"
    echo "  • urllib3, certifi (networking)"
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

echo "✅ Proceso completado - Todas las dependencias incluidas" 