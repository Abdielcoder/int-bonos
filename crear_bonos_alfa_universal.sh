#!/bin/bash

# Script UNIVERSAL para crear ejecutable bonosAlfa compatible con Intel y Apple Silicon
# Soluciona problemas de seguridad y compatibilidad de macOS
# Uso: ./crear_bonos_alfa_universal.sh

set -e  # Salir si hay algún error

# Configuración para bonosAlfa Universal
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
DMG_NAME="bonosAlfa-${APP_VERSION}-universal"
ICON_PATH="assets/img/logo.png"

echo "🚀 Creando bonosAlfa UNIVERSAL para macOS"
echo "📱 Versión: $APP_VERSION"
echo "💻 Compatible: Intel + Apple Silicon (M1/M2/M3)"
echo "🔒 Con firma de código para evitar bloqueos de seguridad"

# Detectar arquitectura actual
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    echo "🍎 Detectado: Apple Silicon (M1/M2/M3)"
    TARGET_ARCH="universal2"
elif [[ "$ARCH" == "x86_64" ]]; then
    echo "💻 Detectado: Intel Mac"
    TARGET_ARCH="universal2"
else
    echo "⚠️ Arquitectura desconocida: $ARCH"
    TARGET_ARCH="universal2"
fi

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
echo "✅ Python3 disponible"

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

# Pillow para iconos
if ! python3 -c "import PIL" 2>/dev/null; then
    echo "📦 Instalando Pillow..."
    pip3 install Pillow
fi

echo "✅ Todas las herramientas están listas"

# Preparar icono universal
echo "🎨 Preparando icono universal..."
if [[ -f "$ICON_PATH" ]]; then
    ICONSET_PATH="assets/img/universal.iconset"
    ICNS_PATH="assets/img/universal.icns"
    
    mkdir -p "$ICONSET_PATH"
    
    # Crear todos los tamaños necesarios para compatibilidad universal
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
    echo "✅ Icono universal creado"
else
    echo "⚠️ No se encontró icono, continuando sin él"
    ICNS_PATH=""
fi

# Crear archivo spec UNIVERSAL
echo "🏗️ Creando configuración UNIVERSAL..."

cat > "bonosAlfa_universal.spec" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-
# Configuración UNIVERSAL para bonosAlfa (Intel + Apple Silicon)

import os
import sys

block_cipher = None

# Lista COMPLETA de imports ocultos (compatible con todas las arquitecturas)
hidden_imports = [
    # Encodings CRÍTICOS
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
    
    # Módulos críticos de Python
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

# Crear ejecutable universal (onedir para mejor compatibilidad)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bonosAlfa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Deshabilitado para mejor compatibilidad universal
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',  # UNIVERSAL: Intel + Apple Silicon
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
    upx=False,  # Deshabilitado para compatibilidad
    upx_exclude=[],
    name='bonosAlfa',
)

# Crear bundle .app UNIVERSAL
app = BUNDLE(
    coll,
    name='bonosAlfa.app',
    icon='assets/img/universal.icns' if os.path.exists('assets/img/universal.icns') else None,
    bundle_identifier='com.rinorisk.bonos.alfa',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Bonos Alfa',
        'CFBundleDisplayName': 'Bonos Alfa',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
        'LSArchitecturePriority': ['arm64', 'x86_64'],  # Preferir Apple Silicon, fallback Intel
        'LSRequiresNativeExecution': False,  # Permitir Rosetta si es necesario
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Excel Files',
                'CFBundleTypeExtensions': ['xlsx', 'xls'],
                'CFBundleTypeRole': 'Editor'
            }
        ],
        # Permisos de seguridad
        'NSAppleEventsUsageDescription': 'Esta aplicación necesita acceso para funcionar correctamente.',
        'NSSystemAdministrationUsageDescription': 'Para acceder a funciones administrativas.',
    },
)
EOF

# Construir la aplicación universal
echo "🔨 Construyendo bonosAlfa UNIVERSAL..."
echo "   ⏳ Esto puede tomar varios minutos..."

python3 -m PyInstaller "bonosAlfa_universal.spec" --clean --noconfirm --log-level WARN

# Verificar que se creó
if [[ ! -d "dist/bonosAlfa.app" ]]; then
    echo "❌ Error: No se pudo crear bonosAlfa.app"
    exit 1
fi

echo "✅ bonosAlfa.app universal creado"

# Verificar arquitecturas soportadas
echo "🔍 Verificando compatibilidad de arquitecturas..."
EXECUTABLE_PATH="dist/bonosAlfa.app/Contents/MacOS/bonosAlfa"
if [[ -f "$EXECUTABLE_PATH" ]]; then
    ARCHS=$(lipo -archs "$EXECUTABLE_PATH" 2>/dev/null || echo "single")
    echo "   📱 Arquitecturas soportadas: $ARCHS"
else
    echo "   ⚠️ No se pudo verificar arquitecturas"
fi

# Intentar firmar la aplicación para evitar problemas de seguridad
echo "🔒 Intentando firmar la aplicación..."
if command -v codesign &> /dev/null; then
    # Firmar con certificado adhoc (sin desarrollador registrado)
    codesign --force --deep --sign - "dist/bonosAlfa.app" 2>/dev/null && {
        echo "✅ Aplicación firmada con certificado adhoc"
    } || {
        echo "⚠️ No se pudo firmar automáticamente"
        echo "   💡 Esto puede causar avisos de seguridad en macOS"
    }
else
    echo "⚠️ codesign no disponible"
fi

# Crear ejecutable directo también
EJECUTABLE_DIR_PATH="dist/bonosAlfa/bonosAlfa"
if [[ -f "$EJECUTABLE_DIR_PATH" ]]; then
    cp "$EJECUTABLE_DIR_PATH" "dist/bonosAlfa_universal"
    chmod +x "dist/bonosAlfa_universal"
    echo "✅ Ejecutable directo creado: dist/bonosAlfa_universal"
fi

# Crear DMG universal
echo "📦 Creando instalador DMG universal..."

if command -v create-dmg &> /dev/null; then
    echo "🎨 Usando create-dmg..."
    
    create-dmg \
        --volname "$APP_DISPLAY_NAME Universal" \
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
        hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME Universal" "$TEMP_DMG"
        
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
    hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME Universal" "$TEMP_DMG"
    
    MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')
    
    cp -R "dist/bonosAlfa.app" "$MOUNT_POINT/"
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    hdiutil unmount "$MOUNT_POINT"
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
fi

# Mostrar resultados
echo ""
echo "🎉 ¡bonosAlfa UNIVERSAL creado exitosamente!"
echo "="*70

if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo "📦 Instalador DMG: dist/$DMG_NAME.dmg ($DMG_SIZE)"
fi

if [[ -d "dist/bonosAlfa.app" ]]; then
    APP_SIZE=$(du -h "dist/bonosAlfa.app" | cut -f1)
    echo "📱 Aplicación Universal: dist/bonosAlfa.app ($APP_SIZE)"
fi

if [[ -f "dist/bonosAlfa_universal" ]]; then
    BIN_SIZE=$(du -h "dist/bonosAlfa_universal" | cut -f1)
    echo "⚙️ Ejecutable directo: dist/bonosAlfa_universal ($BIN_SIZE)"
fi

echo ""
echo "📋 INSTRUCCIONES DE INSTALACIÓN:"
echo "="*70
echo "🍎 Para instalar en macOS (Intel + Apple Silicon):"
echo "   1. Abre $DMG_NAME.dmg"
echo "   2. Arrastra bonosAlfa.app a Applications"
echo "   3. Ejecuta desde Launchpad"
echo ""
echo "🔒 Si aparece aviso de seguridad:"
echo "   1. Ve a Preferencias del Sistema > Seguridad y Privacidad"
echo "   2. Haz clic en 'Abrir de todas formas'"
echo "   3. O ejecuta: xattr -d com.apple.quarantine 'dist/bonosAlfa.app'"
echo ""
echo "🔧 Para ejecutar desde terminal:"
echo "   • ./dist/bonosAlfa_universal"
echo ""
echo "✅ Características UNIVERSALES:"
echo "   • Compatible con Intel Mac y Apple Silicon (M1/M2/M3)"
echo "   • Módulo encodings incluido correctamente"
echo "   • Configuración onedir estable"
echo "   • Firma de código adhoc para reducir avisos"
echo "   • Todas las dependencias incluidas"

# Crear script para resolver problemas de seguridad
echo ""
echo "🛠️ Creando script de ayuda para problemas de seguridad..."

cat > "solucionar_seguridad_mac.sh" << 'EOF'
#!/bin/bash
# Script para solucionar problemas de seguridad con bonosAlfa.app

echo "🔒 Solucionando problemas de seguridad de macOS..."

if [[ -d "dist/bonosAlfa.app" ]]; then
    echo "📱 Removiendo quarantine de bonosAlfa.app..."
    xattr -d com.apple.quarantine "dist/bonosAlfa.app" 2>/dev/null || echo "   (Ya no tenía quarantine)"
    
    echo "🔏 Intentando firmar nuevamente..."
    codesign --force --deep --sign - "dist/bonosAlfa.app" 2>/dev/null && {
        echo "✅ Aplicación firmada exitosamente"
    } || {
        echo "⚠️ No se pudo firmar (puede requerir permisos)"
    }
    
    echo "✅ Intentos de solución completados"
    echo "💡 Si sigue sin funcionar:"
    echo "   1. Click derecho en bonosAlfa.app > Abrir"
    echo "   2. O ve a Preferencias > Seguridad > 'Abrir de todas formas'"
else
    echo "❌ No se encontró dist/bonosAlfa.app"
fi
EOF

chmod +x "solucionar_seguridad_mac.sh"
echo "✅ Script creado: solucionar_seguridad_mac.sh"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__
if [[ -f "assets/img/universal.icns" ]]; then
    rm "assets/img/universal.icns"
fi

echo ""
echo "✅ ¡Proceso UNIVERSAL completado!"
echo "🚀 bonosAlfa está listo para Intel y Apple Silicon" 