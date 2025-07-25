#!/bin/bash

# Script COMPATIBLE LIMPIO para crear ejecutable bonosAlfa sin conflictos Qt
# Resuelve problemas de múltiples frameworks Qt instalados
# Uso: ./crear_bonos_alfa_compatible_limpio.sh

set -e  # Salir si hay algún error

# Configuración para bonosAlfa Compatible Limpio
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
ICON_PATH="assets/img/logo.png"

echo "🚀 Creando bonosAlfa COMPATIBLE LIMPIO para macOS"
echo "📱 Versión: $APP_VERSION"
echo "🔧 Resolviendo conflictos de Qt frameworks"

# Detectar arquitectura actual
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "🍎 Detectado: Apple Silicon (M1/M2/M3)"
    DMG_NAME="bonosAlfa-${APP_VERSION}-CompatibleLimpio"
    ARCH_NAME="CompatibleLimpio"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "💻 Detectado: Intel Mac"
    DMG_NAME="bonosAlfa-${APP_VERSION}-CompatibleLimpio"
    ARCH_NAME="CompatibleLimpio"
else
    echo "⚠️ Arquitectura desconocida: $ARCH"
    DMG_NAME="bonosAlfa-${APP_VERSION}-CompatibleLimpio"
    ARCH_NAME="CompatibleLimpio"
fi

echo "🔒 Con exclusión específica de frameworks Qt conflictivos"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec __pycache__ *.app *.dmg

# Verificar herramientas necesarias
echo "🔍 Verificando herramientas..."

# Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION disponible"

# Verificar frameworks Qt instalados
echo "📦 Verificando frameworks Qt instalados..."
QT_FRAMEWORKS=$(pip list | grep -E "PyQt|PySide" || echo "")
echo "   Frameworks detectados:"
echo "$QT_FRAMEWORKS" | sed 's/^/     /'

# PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# PySide6 (framework preferido)
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📦 Instalando PySide6..."
    pip3 install PySide6
fi

echo "✅ Todas las herramientas están listas"

# Preparar icono si existe
echo "🎨 Preparando icono..."
if [[ -f "$ICON_PATH" ]]; then
    ICONSET_PATH="assets/img/compatible_limpio.iconset"
    ICNS_PATH="assets/img/compatible_limpio.icns"
    
    mkdir -p "$ICONSET_PATH"
    
    # Crear iconos en tamaños estándar
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
    echo "✅ Icono preparado"
    ICON_FLAG="--icon $ICNS_PATH"
else
    echo "⚠️ No se encontró icono, continuando sin él"
    ICNS_PATH=""
    ICON_FLAG=""
fi

# Crear archivo spec COMPATIBLE LIMPIO (sin conflictos Qt)
echo "🏗️ Creando configuración COMPATIBLE LIMPIA..."

cat > "bonosAlfa_compatible_limpio.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Configuración COMPATIBLE LIMPIA para bonosAlfa (sin conflictos Qt)

import os
import sys

block_cipher = None

# Lista ESPECÍFICA de imports ocultos (solo PySide6, NO otros Qt)
hidden_imports = [
    # Encodings CRÍTICOS
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.cp1252',
    'encodings.idna',
    'encodings.aliases',
    'encodings.raw_unicode_escape',
    'encodings.unicode_escape',
    
    # SOLO PySide6 - Framework Qt ESPECÍFICO
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'shiboken6',
    
    # Módulos críticos de Python
    'zipimport',
    'importlib',
    'importlib.util',
    'importlib.machinery',
    'importlib.abc',
    'importlib._bootstrap',
    'importlib._bootstrap_external',
    'collections',
    'collections.abc',
    'functools',
    'operator',
    'itertools',
    'copy',
    'pickle',
    'copyreg',
    '_pickle',
    
    # Data processing
    'pandas',
    'pandas.core',
    'pandas.core.arrays',
    'pandas.core.arrays.integer',
    'pandas.core.arrays.string_',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.excel',
    'pandas._libs',
    'pandas._libs.tslibs',
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'numpy._globals',
    'numpy.random',
    
    # File handling
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.styles',
    'xlsxwriter',
    'xlsxwriter.workbook',
    'xlsxwriter.worksheet',
    
    # Network
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'urllib3.poolmanager',
    'certifi',
    'ssl',
    'socket',
    'http',
    'http.client',
    'http.server',
    
    # Text processing
    'charset_normalizer',
    'idna',
    're',
    'string',
    'unicodedata',
    'codecs',
    
    # Date and time
    'datetime',
    'dateutil',
    'dateutil.parser',
    'dateutil.tz',
    'pytz',
    'time',
    'calendar',
    '_strptime',
    
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
    'math',
    'decimal',
    'fractions',
    'random',
    'shutil',
    'glob',
    'fnmatch',
    'stat',
    'traceback',
    'logging',
    'warnings',
    'inspect',
    'weakref',
    'gc',
    'atexit',
    
    # Crypto y seguridad
    'hashlib',
    'secrets',
    'uuid',
    'binascii',
    'zlib',
    
    # XML y HTML
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    'html',
    'html.parser',
]

# Incluir archivos de datos
datas = [
    ('principal.py', '.'),
    ('assets', 'assets'),
]

# Verificar archivos opcionales
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
        # EXCLUSIÓN ESPECÍFICA de otros frameworks Qt
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PySide2',
        'PySide2.QtCore',
        'PySide2.QtGui',
        'PySide2.QtWidgets',
        'shiboken2',
        'PyQt5.sip',
        
        # Otros módulos no necesarios
        'tkinter',
        'matplotlib',
        'scipy',
        'IPython',
        'notebook',
        'jupyter',
        'pytest',
        'sphinx',
        'django',
        'flask',
        'nicegui',
        'fastapi',
        'test',
        'tests',
        'unittest',
        'distutils',
        'setuptools',
        'pip',
        'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Crear ejecutable (onedir para mejor estabilidad)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bonosAlfa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Deshabilitado para evitar problemas
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Usar arquitectura nativa
    codesign_identity=None,
    entitlements_file=None,
)

# Recopilar archivos
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='bonosAlfa',
)

# Crear bundle .app
app = BUNDLE(
    coll,
    name='bonosAlfa.app',
    icon='assets/img/compatible_limpio.icns' if os.path.exists('assets/img/compatible_limpio.icns') else None,
    bundle_identifier='com.rinorisk.bonos.alfa',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Bonos Alfa',
        'CFBundleDisplayName': 'Bonos Alfa',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'LSRequiresNativeExecution': False,
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Excel Files',
                'CFBundleTypeExtensions': ['xlsx', 'xls'],
                'CFBundleTypeRole': 'Editor'
            }
        ],
        # Permisos adicionales
        'NSAppleEventsUsageDescription': 'Esta aplicación procesa datos de bonos financieros.',
        'NSSystemAdministrationUsageDescription': 'Para acceder a funciones de análisis.',
        'CFBundleExecutable': 'bonosAlfa',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'BALF',
        'LSApplicationCategoryType': 'public.app-category.finance',
        'NSHumanReadableCopyright': 'Copyright © 2024 RinoRisk. Todos los derechos reservados.',
    },
)
EOF

# Construir la aplicación con exclusiones específicas
echo "🔨 Construyendo bonosAlfa COMPATIBLE LIMPIO..."
echo "   ⏳ Esto puede tomar varios minutos..."
echo "   🔧 Excluyendo frameworks Qt conflictivos..."

python3 -m PyInstaller "bonosAlfa_compatible_limpio.spec" --clean --noconfirm --log-level WARN

# Verificar que se creó
if [[ ! -d "dist/bonosAlfa.app" ]]; then
    echo "❌ Error: No se pudo crear bonosAlfa.app"
    exit 1
fi

echo "✅ bonosAlfa.app creado exitosamente"

# Verificar arquitectura del ejecutable
echo "🔍 Verificando arquitectura..."
EXECUTABLE_PATH="dist/bonosAlfa.app/Contents/MacOS/bonosAlfa"
if [[ -f "$EXECUTABLE_PATH" ]]; then
    ARCH_INFO=$(file "$EXECUTABLE_PATH" | cut -d: -f2)
    echo "   📱 Información del ejecutable:$ARCH_INFO"
else
    echo "   ⚠️ No se pudo verificar el ejecutable"
fi

# Firmar la aplicación para reducir problemas de seguridad
echo "🔒 Optimizando seguridad de la aplicación..."

# Remover quarantine attributes
xattr -cr "dist/bonosAlfa.app" 2>/dev/null || echo "   (Sin atributos quarantine)"

# Intentar firmar con certificado adhoc
if command -v codesign &> /dev/null; then
    echo "🔏 Firmando aplicación..."
    
    # Firmar todos los binarios internos primero
    find "dist/bonosAlfa.app" -type f \( -name "*.so" -o -name "*.dylib" \) -exec codesign --force --sign - {} \; 2>/dev/null
    
    # Firmar el ejecutable principal
    codesign --force --deep --sign - "dist/bonosAlfa.app" 2>/dev/null && {
        echo "✅ Aplicación firmada con certificado adhoc"
        
        # Verificar firma
        codesign --verify --verbose "dist/bonosAlfa.app" 2>/dev/null && {
            echo "✅ Firma verificada correctamente"
        } || {
            echo "⚠️ Advertencia en la verificación de firma"
        }
    } || {
        echo "⚠️ No se pudo firmar automáticamente"
    }
else
    echo "⚠️ codesign no disponible"
fi

# Crear ejecutable directo
EJECUTABLE_DIR_PATH="dist/bonosAlfa/bonosAlfa"
if [[ -f "$EJECUTABLE_DIR_PATH" ]]; then
    cp "$EJECUTABLE_DIR_PATH" "dist/bonosAlfa_${ARCH_NAME}"
    chmod +x "dist/bonosAlfa_${ARCH_NAME}"
    echo "✅ Ejecutable directo creado: dist/bonosAlfa_${ARCH_NAME}"
fi

# Crear DMG
echo "📦 Creando instalador DMG..."

if command -v create-dmg &> /dev/null; then
    echo "🎨 Usando create-dmg..."
    
    create-dmg \
        --volname "$APP_DISPLAY_NAME $ARCH_NAME" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "bonosAlfa.app" 175 190 \
        --hide-extension "bonosAlfa.app" \
        --app-drop-link 425 190 \
        --no-internet-enable \
        "dist/$DMG_NAME.dmg" \
        "dist/bonosAlfa.app" 2>/dev/null || {
        echo "⚠️ Error con create-dmg, usando hdiutil..."
        
        # Fallback a hdiutil
        APP_SIZE=$(du -sm "dist/bonosAlfa.app" | cut -f1)
        DMG_SIZE=$((APP_SIZE + 100))
        
        TEMP_DMG="dist/temp_$DMG_NAME.dmg"
        hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME $ARCH_NAME" "$TEMP_DMG"
        
        MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
        
        cp -R "dist/bonosAlfa.app" "$MOUNT_POINT/"
        ln -s /Applications "$MOUNT_POINT/Applications"
        
        hdiutil unmount "$MOUNT_POINT"
        hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
        rm "$TEMP_DMG"
    }
else
    echo "🔧 Usando hdiutil..."
    
    APP_SIZE=$(du -sm "dist/bonosAlfa.app" | cut -f1)
    DMG_SIZE=$((APP_SIZE + 100))
    
    TEMP_DMG="dist/temp_$DMG_NAME.dmg"
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME $ARCH_NAME" "$TEMP_DMG"
    
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    cp -R "dist/bonosAlfa.app" "$MOUNT_POINT/"
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    hdiutil unmount "$MOUNT_POINT"
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Mostrar resultados
echo ""
echo "🎉 ¡bonosAlfa COMPATIBLE LIMPIO creado exitosamente!"
echo "="*70

echo "📊 Arquitectura: $ARCH_NAME ($ARCH)"
echo "🔧 Framework Qt: Solo PySide6 (sin conflictos)"

if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo "📦 Instalador DMG: dist/$DMG_NAME.dmg ($DMG_SIZE)"
fi

if [[ -d "dist/bonosAlfa.app" ]]; then
    APP_SIZE=$(du -h "dist/bonosAlfa.app" | cut -f1)
    echo "📱 Aplicación macOS: dist/bonosAlfa.app ($APP_SIZE)"
fi

if [[ -f "dist/bonosAlfa_${ARCH_NAME}" ]]; then
    BIN_SIZE=$(du -h "dist/bonosAlfa_${ARCH_NAME}" | cut -f1)
    echo "⚙️ Ejecutable directo: dist/bonosAlfa_${ARCH_NAME} ($BIN_SIZE)"
fi

echo ""
echo "📋 INSTRUCCIONES DE INSTALACIÓN:"
echo "="*70
echo "🍎 Para instalar en macOS:"
echo "   1. Abre $DMG_NAME.dmg"
echo "   2. Arrastra bonosAlfa.app a Applications"
echo "   3. Ejecuta desde Launchpad"
echo ""
echo "🔒 Si aparece 'No se puede abrir' o aviso de seguridad:"
echo "   MÉTODO 1 - Click derecho:"
echo "   1. Click derecho en bonosAlfa.app > Abrir"
echo "   2. Confirma 'Abrir' en el diálogo"
echo ""
echo "   MÉTODO 2 - Terminal:"
echo "   1. Abre Terminal"
echo "   2. Ejecuta: xattr -d com.apple.quarantine '/Applications/bonosAlfa.app'"
echo ""
echo "   MÉTODO 3 - Preferencias:"
echo "   1. Ve a Preferencias del Sistema > Seguridad y Privacidad"
echo "   2. Haz clic en 'Abrir de todas formas'"

echo ""
echo "✅ CARACTERÍSTICAS OPTIMIZADAS:"
echo "   • Sin conflictos de frameworks Qt"
echo "   • Solo PySide6 incluido"
echo "   • Exclusión específica de PyQt5/PyQt6/PySide2"
echo "   • Configuración onedir estable"
echo "   • Todas las dependencias incluidas"
echo "   • Firma de código adhoc aplicada"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__
if [[ -f "assets/img/compatible_limpio.icns" ]]; then
    rm "assets/img/compatible_limpio.icns"
fi

echo ""
echo "✅ ¡Proceso COMPATIBLE LIMPIO completado!"
echo "🚀 bonosAlfa está listo sin conflictos Qt" 