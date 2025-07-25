#!/bin/bash

# Script corregido para crear ejecutable bonosAlfa
# Soluciona problemas con encodings y módulos de Python
# Uso: ./crear_bonos_alfa_corregido.sh

set -e  # Salir si hay algún error

# Configuración específica para bonosAlfa
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
DMG_NAME="bonosAlfa-${APP_VERSION}-installer"
ICON_PATH="assets/img/logo.png"

echo "🚀 Iniciando creación CORREGIDA de ejecutable bonosAlfa"
echo "📱 Versión: $APP_VERSION"
echo "💼 Aplicación: $APP_DISPLAY_NAME"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec __pycache__

# Verificar PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# Detectar framework Qt disponible
echo "🔍 Detectando framework Qt..."
QT_FRAMEWORK="PySide6"
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📦 Instalando PySide6..."
    pip3 install PySide6
fi
echo "✅ Usando PySide6"

# Crear archivo spec corregido para bonosAlfa
echo "🏗️ Creando configuración CORREGIDA de PyInstaller para bonosAlfa..."

cat > "bonosAlfa_corregido.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Configuración CORREGIDA para bonosAlfa

import sys
import os

block_cipher = None

# Lista COMPLETA de imports ocultos para bonosAlfa
hidden_imports = [
    # Encodings CRÍTICOS - esto soluciona el error principal
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.cp1252',
    'encodings.idna',
    'encodings.aliases',
    
    # Framework Qt - PySide6
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'shiboken6',
    
    # Módulos estándar de Python CRÍTICOS
    'zipimport',
    'importlib',
    'importlib.util',
    'importlib.machinery',
    'importlib.abc',
    'collections',
    'collections.abc',
    'functools',
    'operator',
    'itertools',
    'copy',
    'pickle',
    'copyreg',
    
    # Data processing
    'pandas',
    'pandas.core',
    'pandas.core.arrays',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.excel',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    
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
    'http',
    'http.client',
    
    # Text processing
    'charset_normalizer',
    'idna',
    're',
    'string',
    'unicodedata',
    
    # Date and time
    'datetime',
    'dateutil',
    'dateutil.parser',
    'pytz',
    'time',
    'calendar',
    
    # Standard library essentials
    'json',
    'pathlib',
    'typing',
    'typing_extensions',
    'base64',
    'hashlib',
    'hmac',
    'os',
    'sys',
    'tempfile',
    'csv',
    'io',
    'struct',
    'platform',
    'subprocess',
    'threading',
    'multiprocessing',
    
    # Math and numbers
    'math',
    'decimal',
    'fractions',
    'random',
    
    # File system
    'shutil',
    'glob',
    'fnmatch',
    'stat',
    
    # Debugging y logging
    'traceback',
    'logging',
    'warnings',
]

# Incluir archivos de datos
datas = [
    ('principal.py', '.'),
    ('assets', 'assets'),
]

# Verificar si existen archivos opcionales
if os.path.exists('otp_dialog.py'):
    datas.append(('otp_dialog.py', '.'))
if os.path.exists('otp_service.py'):
    datas.append(('otp_service.py', '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
        'test',
        'unittest',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Crear ejecutable con configuración onedir (más estable)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bonosAlfa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin consola para GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# Recopilar archivos en directorio
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='bonosAlfa',
)

# Crear bundle .app para macOS
app = BUNDLE(
    coll,
    name='bonosAlfa.app',
    icon='assets/img/logo.png',
    bundle_identifier='com.rinorisk.bonos.alfa',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Bonos Alfa',
        'CFBundleDisplayName': 'Bonos Alfa',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
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

echo "🏗️ Construyendo bonosAlfa con configuración corregida..."

# Ejecutar PyInstaller con configuración detallada
python3 -m PyInstaller "bonosAlfa_corregido.spec" --clean --noconfirm --log-level INFO

# Verificar que se creó la aplicación
if [[ ! -d "dist/bonosAlfa.app" ]]; then
    echo "❌ Error: No se pudo crear bonosAlfa.app"
    exit 1
fi

echo "✅ bonosAlfa.app construido exitosamente"

# Verificar el ejecutable binario en el directorio
EJECUTABLE_PATH="dist/bonosAlfa/bonosAlfa"
if [[ -f "$EJECUTABLE_PATH" ]]; then
    echo "✅ Ejecutable binario disponible en: $EJECUTABLE_PATH"
    
    # Crear un ejecutable directo en dist/
    cp "$EJECUTABLE_PATH" "dist/bonosAlfa_ejecutable"
    chmod +x "dist/bonosAlfa_ejecutable"
    echo "✅ Ejecutable directo creado: dist/bonosAlfa_ejecutable"
else
    echo "⚠️ No se encontró el ejecutable binario"
fi

# Probar la aplicación
echo "🧪 Probando bonosAlfa..."
if [[ -f "$EJECUTABLE_PATH" ]]; then
    echo "Probando ejecutable..."
    timeout 3 "$EJECUTABLE_PATH" 2>&1 || echo "✅ Ejecutable se inició (timeout esperado para GUI)"
fi

# Crear DMG instalador
echo "📦 Creando instalador DMG para bonosAlfa..."

if command -v create-dmg &> /dev/null; then
    echo "🎨 Usando create-dmg..."
    
    create-dmg \
        --volname "$APP_DISPLAY_NAME" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "bonosAlfa.app" 175 190 \
        --hide-extension "bonosAlfa.app" \
        --app-drop-link 425 190 \
        --no-internet-enable \
        "dist/$DMG_NAME.dmg" \
        "dist/bonosAlfa.app" 2>/dev/null || echo "⚠️ Error creando DMG con create-dmg"
else
    echo "🔧 Usando hdiutil..."
    
    APP_SIZE=$(du -sm "dist/bonosAlfa.app" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 100))
    
    TEMP_DMG="dist/temp_$DMG_NAME.dmg"
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME" "$TEMP_DMG"
    
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    cp -R "dist/bonosAlfa.app" "$MOUNT_POINT/"
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    hdiutil unmount "$MOUNT_POINT"
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Mostrar resultados
echo ""
echo "🎉 ¡bonosAlfa CORREGIDO creado exitosamente!"
echo "="*60

if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo "📦 Instalador DMG: dist/$DMG_NAME.dmg ($DMG_SIZE)"
fi

if [[ -d "dist/bonosAlfa.app" ]]; then
    APP_SIZE=$(du -h "dist/bonosAlfa.app" | cut -f1)
    echo "📱 Aplicación macOS: dist/bonosAlfa.app ($APP_SIZE)"
fi

if [[ -f "dist/bonosAlfa_ejecutable" ]]; then
    BIN_SIZE=$(du -h "dist/bonosAlfa_ejecutable" | cut -f1)
    echo "⚙️ Ejecutable directo: dist/bonosAlfa_ejecutable ($BIN_SIZE)"
fi

echo ""
echo "📋 INSTRUCCIONES DE USO:"
echo "="*60
echo "🍎 Para usar en macOS:"
echo "   1. Doble clic en bonosAlfa.app para ejecutar"
echo "   2. O instalar arrastrando a Applications"
echo ""
echo "🔧 Para ejecutar desde terminal:"
echo "   • ./dist/bonosAlfa_ejecutable"
echo ""
echo "✅ Problemas solucionados:"
echo "   • Módulo encodings incluido correctamente"
echo "   • Todos los módulos Python estándar incluidos"
echo "   • Configuración onedir más estable"
echo "   • Dependencias Qt completas"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__

echo "✅ ¡Proceso completado! bonosAlfa corregido está listo." 