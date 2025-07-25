#!/bin/bash

# Script completo para crear ejecutable bonosAlfa con instalador DMG
# Uso: ./crear_bonos_alfa.sh

set -e  # Salir si hay algún error

# Configuración específica para bonosAlfa
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
DMG_NAME="bonosAlfa-${APP_VERSION}-installer"
ICON_PATH="assets/img/logo.png"

echo "🚀 Iniciando creación de ejecutable bonosAlfa"
echo "📱 Versión: $APP_VERSION"
echo "💼 Aplicación: $APP_DISPLAY_NAME"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Lista de dependencias requeridas para bonosAlfa
REQUIRED_PACKAGES=(
    "PySide6"
    "pandas" 
    "requests"
    "openpyxl"
    "xlsxwriter"
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

echo "🔍 Verificando e instalando dependencias para bonosAlfa..."

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

# Detectar framework Qt disponible
echo "🔍 Detectando framework Qt..."
QT_FRAMEWORK=""
if python3 -c "import PySide6" 2>/dev/null; then
    QT_FRAMEWORK="PySide6"
    echo "✅ Usando PySide6"
else
    echo "❌ No se encontró PySide6"
    echo "Instalando PySide6..."
    pip3 install PySide6
    QT_FRAMEWORK="PySide6"
fi

# Verificar archivos necesarios
echo "📋 Verificando archivos del proyecto..."
if [[ ! -f "main.py" ]]; then
    echo "❌ No se encontró main.py"
    exit 1
fi

if [[ ! -f "principal.py" ]]; then
    echo "❌ No se encontró principal.py"
    exit 1
fi

echo "✅ Archivos del proyecto verificados"

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec __pycache__

# Convertir icono PNG a ICNS para macOS
echo "🎨 Preparando icono para bonosAlfa..."
if [[ -f "$ICON_PATH" ]]; then
    ICONSET_PATH="assets/img/bonos_alfa.iconset"
    ICNS_PATH="assets/img/bonos_alfa.icns"
    
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
    echo "✅ Icono convertido para bonosAlfa"
else
    echo "⚠️ No se encontró el icono en $ICON_PATH"
    ICON_FLAG=""
fi

# Crear archivo spec específico para bonosAlfa
echo "🏗️ Creando configuración de PyInstaller para bonosAlfa..."

cat > "bonosAlfa.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-
# Configuración específica para bonosAlfa

block_cipher = None

# Framework Qt detectado: $QT_FRAMEWORK
QT_FRAMEWORK = "$QT_FRAMEWORK"

# Lista completa de imports ocultos para bonosAlfa
hidden_imports = [
    # Framework Qt
    QT_FRAMEWORK,
    f'{QT_FRAMEWORK}.QtCore',
    f'{QT_FRAMEWORK}.QtGui', 
    f'{QT_FRAMEWORK}.QtWidgets',
    f'{QT_FRAMEWORK}.QtNetwork',
    
    # Data processing
    'pandas',
    'pandas.core',
    'pandas.core.arrays',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.excel',
    'numpy',
    
    # File handling
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'xlsxwriter',
    
    # Network
    'requests',
    'requests.adapters',
    'urllib3',
    'urllib3.util',
    'certifi',
    'ssl',
    'socket',
    
    # Text processing
    'charset_normalizer',
    'idna',
    
    # Date and time
    'datetime',
    'dateutil',
    'dateutil.parser',
    'pytz',
    
    # Standard library essentials
    'json',
    'pathlib',
    'typing',
    'typing_extensions',
    'collections',
    'functools',
    'base64',
    'hashlib',
    'os',
    'sys',
    'tempfile',
    'csv',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('principal.py', '.'),
        ('otp_dialog.py', '.'),
        ('otp_service.py', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
         excludes=[
         'tkinter',
         'matplotlib',
         'scipy',
         'IPython',
         'notebook',
         'pytest',
         'sphinx',
         'django',
         'flask',
         'nicegui',
         'fastapi',
         'PyQt6',
         'PyQt5',
         'PySide2',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='$APP_NAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Crear bundle .app para macOS
app = BUNDLE(
    exe,
    name='$APP_NAME.app',
    icon='assets/img/bonos_alfa.icns',
    bundle_identifier='com.rinorisk.bonos.alfa',
    version='$APP_VERSION',
    info_plist={
        'CFBundleName': '$APP_DISPLAY_NAME',
        'CFBundleDisplayName': '$APP_DISPLAY_NAME',
        'CFBundleVersion': '$APP_VERSION',
        'CFBundleShortVersionString': '$APP_VERSION',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Excel Files',
                'CFBundleTypeExtensions': ['xlsx', 'xls'],
                'CFBundleTypeRole': 'Editor'
            }
        ]
    },
)
EOF

echo "🏗️ Construyendo bonosAlfa..."

# Ejecutar PyInstaller
python3 -m PyInstaller "bonosAlfa.spec" --clean --noconfirm --log-level INFO

# Verificar que se creó la aplicación
if [[ ! -d "dist/$APP_NAME.app" ]]; then
    echo "❌ Error: No se pudo crear bonosAlfa.app"
    exit 1
fi

echo "✅ bonosAlfa.app construido exitosamente"

# Verificar que el ejecutable binario también existe
if [[ -f "dist/$APP_NAME" ]]; then
    echo "✅ Ejecutable binario bonosAlfa también disponible"
fi

# Crear DMG instalador
echo "📦 Creando instalador DMG para bonosAlfa..."

# Verificar si create-dmg está disponible
if command -v create-dmg &> /dev/null; then
    echo "🎨 Usando create-dmg para diseño avanzado..."
    
    create-dmg \
        --volname "$APP_DISPLAY_NAME" \
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
    DMG_SIZE=$((APP_SIZE + 100))
    
    TEMP_DMG="dist/temp_$DMG_NAME.dmg"
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME" "$TEMP_DMG"
    
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    cp -R "dist/$APP_NAME.app" "$MOUNT_POINT/"
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    hdiutil unmount "$MOUNT_POINT"
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Mostrar resultados
echo ""
echo "🎉 ¡bonosAlfa creado exitosamente!"
echo "="*50

if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo "📦 Instalador DMG: dist/$DMG_NAME.dmg ($DMG_SIZE)"
fi

if [[ -d "dist/$APP_NAME.app" ]]; then
    APP_SIZE=$(du -h "dist/$APP_NAME.app" | cut -f1)
    echo "📱 Aplicación macOS: dist/$APP_NAME.app ($APP_SIZE)"
fi

if [[ -f "dist/$APP_NAME" ]]; then
    BIN_SIZE=$(du -h "dist/$APP_NAME" | cut -f1)
    echo "⚙️ Ejecutable binario: dist/$APP_NAME ($BIN_SIZE)"
fi

echo ""
echo "📋 INSTRUCCIONES DE INSTALACIÓN:"
echo "="*50
echo "🍎 Para instalar en macOS:"
echo "   1. Abre $DMG_NAME.dmg"
echo "   2. Arrastra bonosAlfa.app a Applications"
echo "   3. Ejecuta desde Launchpad"
echo ""
echo "🔧 Para usar el ejecutable directo:"
echo "   • Ejecuta: ./dist/$APP_NAME"
echo "   • O copia a /usr/local/bin/ para acceso global"
echo ""
echo "✅ Dependencias incluidas:"
echo "   • $QT_FRAMEWORK (UI framework)"
echo "   • pandas (procesamiento de datos)"
echo "   • requests (cliente HTTP)"
echo "   • openpyxl, xlsxwriter (archivos Excel)"
echo "   • Todas las dependencias del sistema"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__
if [[ -f "assets/img/bonos_alfa.icns" ]]; then
    rm "assets/img/bonos_alfa.icns"
fi

echo "✅ ¡Proceso completado! bonosAlfa está listo para distribución." 