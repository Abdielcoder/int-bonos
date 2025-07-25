#!/bin/bash

# Script COMPATIBLE para crear ejecutable bonosAlfa con mejor soporte de seguridad
# Funciona en Intel y Apple Silicon (por separado)
# Uso: ./crear_bonos_alfa_compatible.sh

set -e  # Salir si hay algún error

# Configuración para bonosAlfa Compatible
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
ICON_PATH="assets/img/logo.png"

echo "🚀 Creando bonosAlfa COMPATIBLE para macOS"
echo "📱 Versión: $APP_VERSION"

# Detectar arquitectura actual
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "🍎 Detectado: Apple Silicon (M1/M2/M3)"
    DMG_NAME="bonosAlfa-${APP_VERSION}-AppleSilicon"
    ARCH_NAME="AppleSilicon"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "💻 Detectado: Intel Mac"
    DMG_NAME="bonosAlfa-${APP_VERSION}-Intel"
    ARCH_NAME="Intel"
else
    echo "⚠️ Arquitectura desconocida: $ARCH"
    DMG_NAME="bonosAlfa-${APP_VERSION}-macOS"
    ARCH_NAME="macOS"
fi

echo "🔒 Con optimizaciones de seguridad para evitar bloqueos"

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

# PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller..."
    pip3 install pyinstaller
fi

# PySide6
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📦 Instalando PySide6..."
    pip3 install PySide6
fi

echo "✅ Todas las herramientas están listas"

# Preparar icono si existe
echo "🎨 Preparando icono..."
if [[ -f "$ICON_PATH" ]]; then
    # Intentar instalar Pillow solo si no está
    if ! python3 -c "import PIL" 2>/dev/null; then
        echo "📦 Instalando Pillow para conversión de iconos..."
        pip3 install Pillow
    fi
    
    ICONSET_PATH="assets/img/compatible.iconset"
    ICNS_PATH="assets/img/compatible.icns"
    
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

# Crear archivo spec COMPATIBLE
echo "🏗️ Creando configuración COMPATIBLE..."

cat > "bonosAlfa_compatible.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Configuración COMPATIBLE para bonosAlfa

import os
import sys

block_cipher = None

# Lista COMPLETA de imports ocultos
hidden_imports = [
    # Encodings CRÍTICOS - soluciona problema de cierre
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.cp1252',
    'encodings.idna',
    'encodings.aliases',
    'encodings.raw_unicode_escape',
    'encodings.unicode_escape',
    
    # Framework Qt - PySide6
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
        # Excluir solo lo que definitivamente no necesitamos
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
        'PyQt6',
        'PyQt5',
        'PySide2',
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
    icon='assets/img/compatible.icns' if os.path.exists('assets/img/compatible.icns') else None,
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
        # Permisos adicionales para evitar bloqueos
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

# Construir la aplicación
echo "🔨 Construyendo bonosAlfa COMPATIBLE..."
echo "   ⏳ Esto puede tomar varios minutos..."

python3 -m PyInstaller "bonosAlfa_compatible.spec" --clean --noconfirm --log-level WARN

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
echo "🎉 ¡bonosAlfa COMPATIBLE creado exitosamente!"
echo "="*70

echo "📊 Arquitectura: $ARCH_NAME ($ARCH)"

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
echo "🍎 Para instalar en macOS $ARCH_NAME:"
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
echo "🔧 Para ejecutar desde terminal:"
echo "   • ./dist/bonosAlfa_${ARCH_NAME}"
echo ""
echo "✅ Características OPTIMIZADAS:"
echo "   • Compatible con $ARCH_NAME Mac"
echo "   • Módulos encodings completos incluidos"
echo "   • Firma de código adhoc aplicada"
echo "   • Configuración onedir estable"
echo "   • Todas las dependencias incluidas"

# Crear script de ayuda para problemas de seguridad
echo ""
echo "🛠️ Creando script de ayuda..."

cat > "abrir_bonos_alfa.sh" << EOF
#!/bin/bash
# Script de ayuda para abrir bonosAlfa sin problemas de seguridad

echo "🔓 Abriendo bonosAlfa sin restricciones de seguridad..."

APP_PATH="dist/bonosAlfa.app"
if [[ -d "\$APP_PATH" ]]; then
    echo "📱 Removiendo restricciones de quarantine..."
    xattr -d com.apple.quarantine "\$APP_PATH" 2>/dev/null || echo "   (Sin restricciones previas)"
    
    echo "🚀 Abriendo bonosAlfa..."
    open "\$APP_PATH"
    
    echo "✅ bonosAlfa se está abriendo..."
    echo "💡 Si sigue sin funcionar, ejecuta en Terminal:"
    echo "   sudo spctl --master-disable"
    echo "   (Esto desactiva Gatekeeper temporalmente)"
else
    echo "❌ No se encontró \$APP_PATH"
    echo "💡 Asegúrate de ejecutar este script desde la carpeta del proyecto"
fi
EOF

chmod +x "abrir_bonos_alfa.sh"
echo "✅ Script de ayuda creado: abrir_bonos_alfa.sh"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__
if [[ -f "assets/img/compatible.icns" ]]; then
    rm "assets/img/compatible.icns"
fi

echo ""
echo "✅ ¡Proceso COMPATIBLE completado!"
echo "🚀 bonosAlfa está listo para $ARCH_NAME"
echo ""
echo "💡 RECORDATORIO: Si tienes problemas de seguridad:"
echo "   • Ejecuta: ./abrir_bonos_alfa.sh"
echo "   • O haz click derecho > Abrir en bonosAlfa.app" 