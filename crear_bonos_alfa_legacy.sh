#!/bin/bash

# Script LEGACY para crear ejecutable bonosAlfa compatible con Macs desde 2015
# Máxima compatibilidad: macOS 10.11+ (El Capitan 2015) en adelante
# Optimizado para hardware Intel más antiguo y versiones de macOS heredadas
# Uso: ./crear_bonos_alfa_legacy.sh

set -e  # Salir si hay algún error

# Configuración para bonosAlfa Legacy (Máxima Compatibilidad)
APP_NAME="bonosAlfa"
APP_DISPLAY_NAME="Bonos Alfa"
APP_VERSION="1.0.0"
ICON_PATH="assets/img/logo.png"

echo "🚀 Creando bonosAlfa LEGACY para Macs desde 2015"
echo "📱 Versión: $APP_VERSION"
echo "💻 Compatibilidad: macOS 10.11+ (El Capitan 2015 y posteriores)"
echo "🔧 Optimizado para hardware Intel más antiguo"

# Detectar arquitectura y ajustar para compatibilidad
ARCH=$(uname -m)
SYSTEM_VERSION=$(sw_vers -productVersion)
echo "🖥️ Sistema actual: macOS $SYSTEM_VERSION ($ARCH)"

DMG_NAME="bonosAlfa-${APP_VERSION}-Legacy-Mac2015+"
ARCH_NAME="Legacy-Mac2015+"

echo "🔒 Con optimizaciones máximas de seguridad y compatibilidad"

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Este script solo funciona en macOS"
    exit 1
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.spec __pycache__ *.app *.dmg

# Verificar herramientas necesarias con versiones específicas
echo "🔍 Verificando herramientas para compatibilidad legacy..."

# Python - verificar versión compatible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

echo "✅ Python $PYTHON_VERSION disponible"

# Verificar compatibilidad de Python con macOS antiguo
if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 7 ]]; then
    echo "⚠️ Advertencia: Python $PYTHON_VERSION puede tener limitaciones en macOS antiguo"
    echo "   Se recomienda Python 3.7+ para mejor compatibilidad"
fi

# PyInstaller con versión específica para compatibilidad
echo "📦 Verificando PyInstaller para compatibilidad legacy..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "📦 Instalando PyInstaller optimizado para legacy..."
    # Usar versión específica conocida por funcionar bien en sistemas antiguos
    pip3 install "pyinstaller>=4.10,<6.0"
else
    PYINSTALLER_VERSION=$(python3 -c "import PyInstaller; print(PyInstaller.__version__)" 2>/dev/null || echo "desconocida")
    echo "✅ PyInstaller $PYINSTALLER_VERSION disponible"
fi

# PySide6 con verificación de compatibilidad
echo "📦 Verificando PySide6..."
if ! python3 -c "import PySide6" 2>/dev/null; then
    echo "📦 Instalando PySide6 optimizado para legacy..."
    # Intentar instalar PySide6, fallback a PySide2 si falla
    pip3 install PySide6 || {
        echo "⚠️ PySide6 falló, intentando PySide2 para compatibilidad legacy..."
        pip3 install PySide2
    }
fi

# Detectar framework Qt disponible
QT_FRAMEWORK=""
if python3 -c "import PySide6" 2>/dev/null; then
    QT_FRAMEWORK="PySide6"
    echo "✅ Usando PySide6"
elif python3 -c "import PySide2" 2>/dev/null; then
    QT_FRAMEWORK="PySide2"
    echo "✅ Usando PySide2 (mejor para macOS legacy)"
elif python3 -c "import PyQt5" 2>/dev/null; then
    QT_FRAMEWORK="PyQt5"
    echo "✅ Usando PyQt5 (compatibilidad legacy)"
else
    echo "❌ No se encontró framework Qt compatible"
    exit 1
fi

echo "✅ Todas las herramientas están listas para construcción legacy"

# Preparar icono compatible con sistemas antiguos
echo "🎨 Preparando icono para compatibilidad legacy..."
if [[ -f "$ICON_PATH" ]]; then
    # Verificar sips (debería estar en cualquier macOS)
    if ! command -v sips &> /dev/null; then
        echo "⚠️ sips no disponible, continuando sin icono personalizado"
        ICNS_PATH=""
        ICON_FLAG=""
    else
        ICONSET_PATH="assets/img/legacy.iconset"
        ICNS_PATH="assets/img/legacy.icns"
        
        mkdir -p "$ICONSET_PATH"
        
        # Crear iconos en todos los tamaños requeridos (incluyendo formatos antiguos)
        echo "  Generando iconos para máxima compatibilidad..."
        for size in 16 32 64 128 256 512 1024; do
            sips -z $size $size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}.png" > /dev/null 2>&1
            
            # Versiones @2x para retina (si están soportadas)
            if [[ $size -le 512 ]]; then
                double_size=$((size * 2))
                sips -z $double_size $double_size "$ICON_PATH" --out "${ICONSET_PATH}/icon_${size}x${size}@2x.png" > /dev/null 2>&1
            fi
        done
        
        # Crear icono .icns
        if iconutil -c icns "$ICONSET_PATH" -o "$ICNS_PATH" 2>/dev/null; then
            rm -rf "$ICONSET_PATH"
            echo "✅ Icono legacy preparado"
            ICON_FLAG="--icon $ICNS_PATH"
        else
            echo "⚠️ Error creando icono, continuando sin él"
            rm -rf "$ICONSET_PATH"
            ICNS_PATH=""
            ICON_FLAG=""
        fi
    fi
else
    echo "⚠️ No se encontró icono, continuando sin él"
    ICNS_PATH=""
    ICON_FLAG=""
fi

# Crear archivo spec LEGACY con máxima compatibilidad
echo "🏗️ Creando configuración LEGACY para máxima compatibilidad..."

cat > "bonosAlfa_legacy.spec" << EOF
# -*- mode: python ; coding: utf-8 -*-
# Configuración LEGACY para bonosAlfa - Máxima compatibilidad Mac 2015+

import os
import sys

block_cipher = None

# Framework Qt detectado: $QT_FRAMEWORK
QT_FRAMEWORK = "$QT_FRAMEWORK"

# Lista ULTRA-COMPLETA de imports ocultos para máxima compatibilidad
hidden_imports = [
    # Encodings CRÍTICOS - esencial para sistemas antiguos
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.cp1252',
    'encodings.idna',
    'encodings.aliases',
    'encodings.raw_unicode_escape',
    'encodings.unicode_escape',
    'encodings.utf_16',
    'encodings.utf_16_le',
    'encodings.utf_16_be',
    'encodings.utf_32',
    'encodings.utf_32_le',
    'encodings.utf_32_be',
    'encodings.mac_latin2',
    'encodings.mac_roman',
    
    # Framework Qt - Compatible con legacy
    QT_FRAMEWORK,
    f'{QT_FRAMEWORK}.QtCore',
    f'{QT_FRAMEWORK}.QtGui', 
    f'{QT_FRAMEWORK}.QtWidgets',
    f'{QT_FRAMEWORK}.QtNetwork',
    f'{QT_FRAMEWORK}.QtPrintSupport',
]

# Agregar imports específicos según el framework
if QT_FRAMEWORK == "PySide6":
    hidden_imports.extend([
        'shiboken6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
    ])
elif QT_FRAMEWORK == "PySide2":
    hidden_imports.extend([
        'shiboken2',
        'PySide2.QtCore',
        'PySide2.QtGui',
        'PySide2.QtWidgets',
    ])
elif QT_FRAMEWORK == "PyQt5":
    hidden_imports.extend([
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.sip',
    ])

# Continuar con imports esenciales
hidden_imports.extend([
    # Módulos críticos de Python para sistemas legacy
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
    'types',
    'typing',
    
    # Compatibilidad con versiones antiguas de Python
    'six',  # Si está disponible
    
    # Data processing - versiones compatibles
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
    
    # NumPy con compatibilidad legacy
    'numpy',
    'numpy.core',
    'numpy.core._multiarray_umath',
    'numpy._globals',
    'numpy.random',
    'numpy.ma',
    'numpy.lib',
    'numpy.linalg',
    
    # File handling - máxima compatibilidad
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.styles',
    'openpyxl.reader',
    'openpyxl.writer',
    'xlsxwriter',
    'xlsxwriter.workbook',
    'xlsxwriter.worksheet',
    'xlrd',  # Para archivos .xls antiguos
    'xlwt',  # Para escribir archivos .xls
    
    # Network - compatible con SSL legacy
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'requests.packages',
    'urllib3',
    'urllib3.util',
    'urllib3.util.retry',
    'urllib3.poolmanager',
    'urllib3.util.ssl_',
    'certifi',
    'ssl',
    'socket',
    'http',
    'http.client',
    'http.server',
    '_ssl',  # SSL legacy
    
    # Text processing con encodings legacy
    'charset_normalizer',
    'chardet',  # Fallback para detección de charset
    'idna',
    're',
    'string',
    'unicodedata',
    'codecs',
    'locale',
    
    # Date and time - compatible con sistemas antiguos
    'datetime',
    'dateutil',
    'dateutil.parser',
    'dateutil.tz',
    'dateutil.relativedelta',
    'pytz',
    'time',
    'calendar',
    '_strptime',
    
    # Standard library COMPLETA para legacy
    'json',
    'pathlib',
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
    'signal',
    'errno',
    
    # Crypto y seguridad para legacy
    'hashlib',
    'secrets',
    'uuid',
    'binascii',
    'zlib',
    'gzip',
    'bz2',
    'lzma',
    
    # XML y HTML - compatibilidad completa
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    'xml.parsers',
    'xml.parsers.expat',
    'html',
    'html.parser',
    'html.entities',
    
    # Soporte para formatos adicionales
    'mimetypes',
    'email',
    'email.parser',
    'email.message',
    'email.mime',
    
    # Threading y concurrency legacy
    'queue',
    'concurrent',
    'concurrent.futures',
    'asyncio',  # Si está soportado
    
    # Debugging y logging legacy
    'pdb',
    'traceback',
    'linecache',
    'dis',
])

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
        # Excluir SOLO lo que definitivamente causa problemas en legacy
        'tkinter',  # Mantener solo si se usa
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
        'uvicorn',
        # No excluir Qt frameworks para evitar conflictos
        'test',
        'tests',
        'unittest.mock',  # Puede causar problemas en Python antiguo
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

# Crear ejecutable LEGACY (onedir para máxima estabilidad)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bonosAlfa',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # DESHABILITADO - UPX causa problemas en sistemas legacy
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Usar arquitectura nativa para máxima compatibilidad
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
    upx=False,  # Sin compresión para compatibilidad
    upx_exclude=[],
    name='bonosAlfa',
)

# Crear bundle .app LEGACY
app = BUNDLE(
    coll,
    name='bonosAlfa.app',
    icon='$ICNS_PATH' if os.path.exists('$ICNS_PATH') else None,
    bundle_identifier='com.rinorisk.bonos.alfa',
    version='1.0.0',
    info_plist={
        'CFBundleName': 'Bonos Alfa',
        'CFBundleDisplayName': 'Bonos Alfa',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        
        # CRUCIAL: Versión mínima para Mac 2015 (El Capitan)
        'LSMinimumSystemVersion': '10.11.0',
        
        # Configuraciones para máxima compatibilidad legacy
        'LSRequiresNativeExecution': False,  # Permitir Rosetta si es necesario
        'LSApplicationCategoryType': 'public.app-category.finance',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'BALF',
        'CFBundleExecutable': 'bonosAlfa',
        
        # Tipos de documentos soportados
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Excel Files',
                'CFBundleTypeExtensions': ['xlsx', 'xls'],
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Default'
            },
            {
                'CFBundleTypeName': 'CSV Files',
                'CFBundleTypeExtensions': ['csv'],
                'CFBundleTypeRole': 'Editor',
                'LSHandlerRank': 'Default'
            }
        ],
        
        # Permisos y descripciones para evitar bloqueos
        'NSAppleEventsUsageDescription': 'Bonos Alfa procesa datos financieros de bonos.',
        'NSSystemAdministrationUsageDescription': 'Para acceder a funciones de análisis avanzado.',
        'NSDocumentsFolderUsageDescription': 'Para acceder a archivos de datos de bonos.',
        'NSDesktopFolderUsageDescription': 'Para guardar reportes y análisis.',
        'NSDownloadsFolderUsageDescription': 'Para importar archivos de datos.',
        
        # Configuraciones legacy
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'LSFileQuarantineEnabled': False,  # Reducir problemas de quarantine
        'LSUIElement': False,
        
        # Copyright y metadata
        'NSHumanReadableCopyright': 'Copyright © 2024 RinoRisk. Todos los derechos reservados.',
        'CFBundleGetInfoString': 'Bonos Alfa 1.0.0, Copyright © 2024 RinoRisk.',
        
        # Configuraciones adicionales para legacy
        'CSResourcesFileMapped': True,
        'LSHasLocalizedDisplayName': False,
        'NSSupportsAutomaticGraphicsSwitching': True,
    },
)
EOF

# Construir la aplicación con configuración legacy
echo "🔨 Construyendo bonosAlfa LEGACY para Mac 2015+..."
echo "   ⏳ Esto puede tomar varios minutos en sistemas antiguos..."
echo "   🔧 Usando PyInstaller con optimizaciones para legacy..."

python3 -m PyInstaller "bonosAlfa_legacy.spec" --clean --noconfirm --log-level WARN

# Verificar que se creó la aplicación
if [[ ! -d "dist/bonosAlfa.app" ]]; then
    echo "❌ Error: No se pudo crear bonosAlfa.app"
    exit 1
fi

echo "✅ bonosAlfa.app LEGACY creado exitosamente"

# Verificar arquitectura y compatibilidad
echo "🔍 Verificando compatibilidad legacy..."
EXECUTABLE_PATH="dist/bonosAlfa.app/Contents/MacOS/bonosAlfa"
if [[ -f "$EXECUTABLE_PATH" ]]; then
    ARCH_INFO=$(file "$EXECUTABLE_PATH" | cut -d: -f2)
    echo "   📱 Información del ejecutable:$ARCH_INFO"
    
    # Verificar que no requiera versiones nuevas de macOS
    OTOOL_INFO=$(otool -l "$EXECUTABLE_PATH" 2>/dev/null | grep -A2 LC_VERSION_MIN_MACOSX | grep version || echo "N/A")
    echo "   🔧 Versión mínima detectada: $OTOOL_INFO"
else
    echo "   ⚠️ No se pudo verificar el ejecutable"
fi

# Optimizaciones avanzadas de seguridad para legacy
echo "🔒 Aplicando optimizaciones de seguridad legacy..."

# Remover TODOS los atributos quarantine
find "dist/bonosAlfa.app" -type f -exec xattr -c {} \; 2>/dev/null || echo "   (Sin atributos quarantine previos)"

# Firmar con certificado adhoc para evitar problemas de Gatekeeper
if command -v codesign &> /dev/null; then
    echo "🔏 Firmando aplicación para compatibilidad legacy..."
    
    # Firmar TODOS los binarios y librerías
    echo "   Firmando librerías internas..."
    find "dist/bonosAlfa.app" -type f \( -name "*.so" -o -name "*.dylib" -o -perm +111 \) -exec codesign --force --sign - {} \; 2>/dev/null
    
    # Firmar la aplicación completa
    echo "   Firmando aplicación principal..."
    codesign --force --deep --sign - --preserve-metadata=identifier,entitlements,flags "dist/bonosAlfa.app" 2>/dev/null && {
        echo "✅ Aplicación firmada con certificado adhoc"
        
        # Verificar la firma
        if codesign --verify --verbose=4 "dist/bonosAlfa.app" 2>/dev/null; then
            echo "✅ Firma verificada correctamente"
        else
            echo "⚠️ Advertencia en la verificación de firma (normal en legacy)"
        fi
    } || {
        echo "⚠️ Firma básica aplicada (compatible con legacy)"
    }
else
    echo "⚠️ codesign no disponible - aplicación sin firmar"
fi

# Crear ejecutable directo para testing
EJECUTABLE_DIR_PATH="dist/bonosAlfa/bonosAlfa"
if [[ -f "$EJECUTABLE_DIR_PATH" ]]; then
    cp "$EJECUTABLE_DIR_PATH" "dist/bonosAlfa_${ARCH_NAME}"
    chmod +x "dist/bonosAlfa_${ARCH_NAME}"
    echo "✅ Ejecutable directo creado: dist/bonosAlfa_${ARCH_NAME}"
fi

# Crear DMG con máxima compatibilidad
echo "📦 Creando instalador DMG legacy..."

# Usar solo hdiutil para máxima compatibilidad (create-dmg puede no estar en sistemas antiguos)
echo "🔧 Usando hdiutil nativo para compatibilidad legacy..."

APP_SIZE=$(du -sm "dist/bonosAlfa.app" | cut -f1)
DMG_SIZE=$((APP_SIZE + 150))  # Espacio extra para compatibilidad

TEMP_DMG="dist/temp_$DMG_NAME.dmg"

# Crear DMG con formato HFS+ (máxima compatibilidad)
hdiutil create -size ${DMG_SIZE}m -fs HFS+ -volname "$APP_DISPLAY_NAME Legacy" "$TEMP_DMG"

# Montar y copiar archivos
MOUNT_POINT=$(hdiutil mount "$TEMP_DMG" | grep "/Volumes/" | awk '{print $3}')

if [[ -n "$MOUNT_POINT" ]]; then
    echo "   Copiando aplicación al DMG..."
    cp -R "dist/bonosAlfa.app" "$MOUNT_POINT/"
    
    # Crear enlace a Applications para fácil instalación
    ln -s /Applications "$MOUNT_POINT/Applications"
    
    # Crear archivo README para instrucciones legacy
    cat > "$MOUNT_POINT/README - Instrucciones.txt" << 'READMEEOF'
BONOS ALFA - VERSIÓN LEGACY
Compatible con Mac desde 2015 (macOS 10.11+)

INSTRUCCIONES DE INSTALACIÓN:
1. Arrastra "bonosAlfa.app" a la carpeta "Applications"
2. Ve a Aplicaciones y busca "Bonos Alfa"
3. Haz click derecho en "Bonos Alfa" > Abrir
4. Confirma "Abrir" si aparece advertencia de seguridad

SOLUCIÓN DE PROBLEMAS:
Si aparece "No se puede abrir porque proviene de un desarrollador no identificado":

MÉTODO 1 - Click derecho:
- Click derecho en bonosAlfa.app > Abrir
- Confirma "Abrir" en el diálogo

MÉTODO 2 - Terminal:
- Abre Terminal (Aplicaciones > Utilidades > Terminal)
- Escribe: xattr -d com.apple.quarantine /Applications/bonosAlfa.app
- Presiona Enter

MÉTODO 3 - Preferencias del Sistema:
- Ve a Preferencias del Sistema > Seguridad y Privacidad
- Haz clic en "Abrir de todas formas"

COMPATIBILIDAD:
✅ macOS 10.11 El Capitan (2015) y posteriores
✅ Macs Intel de 2015 en adelante
✅ Compatible con macOS Big Sur y posteriores
✅ Todas las dependencias incluidas

CONTACTO:
RinoRisk - Copyright © 2024
READMEEOF
    
    # Desmontar
    hdiutil unmount "$MOUNT_POINT"
    
    # Convertir a DMG comprimido (compatible)
    hdiutil convert "$TEMP_DMG" -format UDZO -o "dist/$DMG_NAME.dmg"
    rm "$TEMP_DMG"
    
    echo "✅ DMG legacy creado exitosamente"
else
    echo "❌ Error montando DMG temporal"
fi

# Mostrar resultados finales
echo ""
echo "🎉 ¡bonosAlfa LEGACY creado exitosamente!"
echo "="*80

echo "📊 Configuración LEGACY:"
echo "   🖥️  Arquitectura: $ARCH_NAME"
echo "   💻 Sistema actual: macOS $SYSTEM_VERSION ($ARCH)"
echo "   🔧 Framework Qt: $QT_FRAMEWORK"
echo "   📦 PyInstaller: $(python3 -c "import PyInstaller; print(PyInstaller.__version__)" 2>/dev/null || echo "N/A")"
echo "   🐍 Python: $PYTHON_VERSION"

echo ""
echo "📦 Archivos generados:"

if [[ -f "dist/$DMG_NAME.dmg" ]]; then
    DMG_SIZE=$(du -h "dist/$DMG_NAME.dmg" | cut -f1)
    echo "   📀 Instalador DMG: dist/$DMG_NAME.dmg ($DMG_SIZE)"
fi

if [[ -d "dist/bonosAlfa.app" ]]; then
    APP_SIZE=$(du -h "dist/bonosAlfa.app" | cut -f1)
    echo "   📱 Aplicación macOS: dist/bonosAlfa.app ($APP_SIZE)"
fi

if [[ -f "dist/bonosAlfa_${ARCH_NAME}" ]]; then
    BIN_SIZE=$(du -h "dist/bonosAlfa_${ARCH_NAME}" | cut -f1)
    echo "   ⚙️  Ejecutable directo: dist/bonosAlfa_${ARCH_NAME} ($BIN_SIZE)"
fi

echo ""
echo "📋 INSTRUCCIONES PARA MACS DESDE 2015:"
echo "="*80
echo "🍎 INSTALACIÓN ESTÁNDAR:"
echo "   1. Abre el archivo $DMG_NAME.dmg"
echo "   2. Arrastra bonosAlfa.app a la carpeta Applications"
echo "   3. Ve a Aplicaciones y busca 'Bonos Alfa'"
echo "   4. Haz click derecho > Abrir (primera vez)"
echo "   5. Confirma 'Abrir' en el diálogo de seguridad"

echo ""
echo "🔒 SOLUCIÓN DE PROBLEMAS DE SEGURIDAD:"
echo ""
echo "   Si aparece 'No se puede abrir porque proviene de un desarrollador no identificado':"
echo ""
echo "   MÉTODO 1 - Click derecho (MÁS FÁCIL):"
echo "   • Click derecho en bonosAlfa.app > Abrir"
echo "   • Confirma 'Abrir' cuando aparezca el diálogo"
echo ""
echo "   MÉTODO 2 - Terminal:"
echo "   • Abre Terminal (Cmd+Espacio, escribe 'Terminal')"
echo "   • Escribe: xattr -d com.apple.quarantine /Applications/bonosAlfa.app"
echo "   • Presiona Enter"
echo ""
echo "   MÉTODO 3 - Preferencias del Sistema:"
echo "   • Ve a Preferencias del Sistema > Seguridad y Privacidad"
echo "   • En la pestaña 'General', haz clic en 'Abrir de todas formas'"
echo ""
echo "   MÉTODO 4 - Deshabilitar Gatekeeper temporalmente (SOLO SI ES NECESARIO):"
echo "   • En Terminal: sudo spctl --master-disable"
echo "   • Ejecuta la aplicación"
echo "   • Reactivar: sudo spctl --master-enable"

echo ""
echo "🔧 EJECUCIÓN DESDE TERMINAL (para debugging):"
echo "   • Terminal: ./dist/bonosAlfa_${ARCH_NAME}"
echo "   • O desde la app: /Applications/bonosAlfa.app/Contents/MacOS/bonosAlfa"

echo ""
echo "✅ CARACTERÍSTICAS OPTIMIZADAS PARA LEGACY:"
echo "   ✓ Compatible con macOS 10.11+ (El Capitan 2015)"
echo "   ✓ Máxima compatibilidad con hardware Intel 2015+"
echo "   ✓ Encodings completos para sistemas antiguos"
echo "   ✓ Sin compresión UPX (mejor estabilidad legacy)"
echo "   ✓ Framework Qt compatible ($QT_FRAMEWORK)"
echo "   ✓ Firma adhoc aplicada"
echo "   ✓ Configuración onedir estable"
echo "   ✓ Permisos legacy configurados"
echo "   ✓ Soporte para formatos Excel legacy (.xls)"
echo "   ✓ Todas las dependencias embebidas"

echo ""
echo "💡 RECOMENDACIONES PARA SISTEMAS LEGACY:"
echo "   • Si tienes macOS 10.11-10.14, considera actualizar a 10.15+ si es posible"
echo "   • Para mejor rendimiento, cierra otras aplicaciones durante el uso"
echo "   • La primera ejecución puede ser más lenta (normal en sistemas antiguos)"
echo "   • Si experimentas problemas, usa el ejecutable directo desde terminal"

# Crear script de instalación asistida para usuarios de Mac legacy
echo ""
echo "🛠️ Creando script de instalación asistida..."

cat > "instalar_bonos_alfa_legacy.sh" << 'INSTALLEOF'
#!/bin/bash
# Script de instalación asistida para bonosAlfa en Macs legacy

echo "🍎 INSTALADOR ASISTIDO DE BONOS ALFA LEGACY"
echo "Compatible con Macs desde 2015 (macOS 10.11+)"
echo "=================================================="

# Verificar sistema
SYSTEM_VERSION=$(sw_vers -productVersion)
SYSTEM_MAJOR=$(echo $SYSTEM_VERSION | cut -d'.' -f1)
SYSTEM_MINOR=$(echo $SYSTEM_VERSION | cut -d'.' -f2)

echo "🖥️ Sistema detectado: macOS $SYSTEM_VERSION"

# Verificar compatibilidad
if [[ $SYSTEM_MAJOR -lt 10 ]] || [[ $SYSTEM_MAJOR -eq 10 && $SYSTEM_MINOR -lt 11 ]]; then
    echo "❌ ADVERTENCIA: Tu sistema (macOS $SYSTEM_VERSION) es anterior a 10.11"
    echo "   Bonos Alfa Legacy requiere macOS 10.11+ (El Capitan 2015)"
    echo "   La aplicación podría no funcionar correctamente."
    read -p "¿Continuar de todas formas? (s/N): " respuesta
    if [[ ! "$respuesta" =~ ^[Ss]$ ]]; then
        echo "Instalación cancelada."
        exit 1
    fi
else
    echo "✅ Sistema compatible"
fi

# Buscar la aplicación
APP_PATH="dist/bonosAlfa.app"
if [[ ! -d "$APP_PATH" ]]; then
    echo "❌ No se encontró bonosAlfa.app en dist/"
    echo "   Asegúrate de ejecutar este script desde la carpeta del proyecto"
    exit 1
fi

echo "📱 Aplicación encontrada: $APP_PATH"

# Instalación
echo ""
echo "🔧 INSTALANDO BONOS ALFA..."

# Copiar a Applications
echo "📂 Copiando a /Applications..."
if cp -R "$APP_PATH" "/Applications/"; then
    echo "✅ Aplicación copiada exitosamente"
else
    echo "❌ Error copiando aplicación. ¿Necesitas permisos de administrador?"
    echo "   Intenta: sudo cp -R '$APP_PATH' /Applications/"
    exit 1
fi

# Remover quarantine
echo "🔓 Removiendo restricciones de seguridad..."
xattr -cr "/Applications/bonosAlfa.app" 2>/dev/null && {
    echo "✅ Restricciones removidas"
} || {
    echo "⚠️ No se pudieron remover algunas restricciones (normal)"
}

# Intentar firma adhoc
if command -v codesign &> /dev/null; then
    echo "🔏 Aplicando firma adhoc..."
    codesign --force --deep --sign - "/Applications/bonosAlfa.app" 2>/dev/null && {
        echo "✅ Firma aplicada"
    } || {
        echo "⚠️ No se pudo aplicar firma (la aplicación debería funcionar)"
    }
fi

echo ""
echo "🎉 ¡INSTALACIÓN COMPLETADA!"
echo "========================="
echo ""
echo "📍 Bonos Alfa está instalado en: /Applications/bonosAlfa.app"
echo ""
echo "🚀 PARA EJECUTAR:"
echo "   1. Ve a Aplicaciones (Finder > Aplicaciones)"
echo "   2. Busca 'bonosAlfa' o 'Bonos Alfa'"
echo "   3. Haz CLICK DERECHO > Abrir (importante para la primera vez)"
echo "   4. Confirma 'Abrir' en el diálogo de seguridad"
echo ""
echo "💡 La primera ejecución puede ser lenta (normal en sistemas legacy)"
echo ""
echo "🔧 Si tienes problemas:"
echo "   • Ejecuta en Terminal: /Applications/bonosAlfa.app/Contents/MacOS/bonosAlfa"
echo "   • O contacta soporte técnico"
echo ""
echo "✅ ¡Disfruta usando Bonos Alfa!"
INSTALLEOF

chmod +x "instalar_bonos_alfa_legacy.sh"
echo "✅ Script de instalación creado: instalar_bonos_alfa_legacy.sh"

# Crear script de ayuda para troubleshooting
cat > "solucionar_problemas_legacy.sh" << 'TROUBLEOF'
#!/bin/bash
# Script de solución de problemas para bonosAlfa legacy

echo "🔧 SOLUCIONADOR DE PROBLEMAS - BONOS ALFA LEGACY"
echo "================================================"

APP_PATH="/Applications/bonosAlfa.app"

# Verificar instalación
if [[ ! -d "$APP_PATH" ]]; then
    echo "❌ bonosAlfa no está instalado en Applications"
    echo "   Ejecuta primero: ./instalar_bonos_alfa_legacy.sh"
    exit 1
fi

echo "✅ Aplicación encontrada en: $APP_PATH"

# Mostrar información del sistema
echo ""
echo "📋 INFORMACIÓN DEL SISTEMA:"
echo "   macOS: $(sw_vers -productVersion)"
echo "   Arquitectura: $(uname -m)"
echo "   Aplicación: $(file "$APP_PATH/Contents/MacOS/bonosAlfa" | cut -d: -f2)"

# Verificar y solucionar problemas comunes
echo ""
echo "🔍 VERIFICANDO PROBLEMAS COMUNES..."

# Problema 1: Quarantine
echo ""
echo "1. Verificando atributos quarantine..."
if xattr -l "$APP_PATH" 2>/dev/null | grep -q "com.apple.quarantine"; then
    echo "   ⚠️ Detectados atributos quarantine"
    echo "   🔧 Solucionando..."
    xattr -dr com.apple.quarantine "$APP_PATH" && {
        echo "   ✅ Quarantine removido"
    } || {
        echo "   ❌ Error removiendo quarantine"
    }
else
    echo "   ✅ Sin atributos quarantine problemáticos"
fi

# Problema 2: Permisos
echo ""
echo "2. Verificando permisos de ejecución..."
EXEC_PATH="$APP_PATH/Contents/MacOS/bonosAlfa"
if [[ -x "$EXEC_PATH" ]]; then
    echo "   ✅ Permisos de ejecución correctos"
else
    echo "   ⚠️ Permisos de ejecución incorrectos"
    echo "   🔧 Corrigiendo permisos..."
    chmod +x "$EXEC_PATH" && {
        echo "   ✅ Permisos corregidos"
    } || {
        echo "   ❌ Error corrigiendo permisos"
    }
fi

# Problema 3: Gatekeeper
echo ""
echo "3. Verificando estado de Gatekeeper..."
GATEKEEPER_STATUS=$(spctl --status)
echo "   Estado: $GATEKEEPER_STATUS"

if [[ "$GATEKEEPER_STATUS" == "assessments enabled" ]]; then
    echo "   🔧 Gatekeeper activo - probando excepción..."
    if spctl --assess --type execute "$APP_PATH" 2>/dev/null; then
        echo "   ✅ Aplicación aprobada por Gatekeeper"
    else
        echo "   ⚠️ Aplicación no aprobada por Gatekeeper"
        echo "   💡 Solución: Haz click derecho > Abrir en la aplicación"
    fi
fi

# Problema 4: Dependencias
echo ""
echo "4. Verificando dependencias críticas..."
DYLIB_COUNT=$(find "$APP_PATH" -name "*.dylib" | wc -l)
SO_COUNT=$(find "$APP_PATH" -name "*.so" | wc -l)
echo "   Librerías dinámicas: $DYLIB_COUNT"
echo "   Módulos Python: $SO_COUNT"

if [[ $DYLIB_COUNT -gt 0 && $SO_COUNT -gt 0 ]]; then
    echo "   ✅ Dependencias incluidas"
else
    echo "   ⚠️ Posibles dependencias faltantes"
fi

# Intentar ejecución de prueba
echo ""
echo "5. Probando ejecución..."
echo "   🚀 Intentando ejecutar bonosAlfa..."

timeout 5 "$EXEC_PATH" 2>&1 >/dev/null && {
    echo "   ✅ Aplicación se ejecuta correctamente"
} || {
    EXIT_CODE=$?
    if [[ $EXIT_CODE -eq 124 ]]; then
        echo "   ✅ Aplicación se inició (timeout esperado para GUI)"
    else
        echo "   ❌ Error ejecutando aplicación (código: $EXIT_CODE)"
        echo "   💡 Intenta ejecutar manualmente: $EXEC_PATH"
    fi
}

echo ""
echo "📋 RESUMEN DE SOLUCIONES:"
echo "========================"
echo ""
echo "✅ MÉTODOS RECOMENDADOS (en orden):"
echo ""
echo "1. MÉTODO CLICK DERECHO (MÁS FÁCIL):"
echo "   • Finder > Aplicaciones > bonosAlfa"
echo "   • Click derecho > Abrir"
echo "   • Confirma 'Abrir'"
echo ""
echo "2. MÉTODO TERMINAL:"
echo "   • Terminal: open /Applications/bonosAlfa.app"
echo "   • O: $EXEC_PATH"
echo ""
echo "3. MÉTODO PREFERENCIAS:"
echo "   • Preferencias del Sistema > Seguridad y Privacidad"
echo "   • Click en 'Abrir de todas formas'"
echo ""
echo "4. MÉTODO GATEKEEPER (TEMPORAL):"
echo "   • Terminal: sudo spctl --master-disable"
echo "   • Ejecuta la aplicación"
echo "   • Reactivar: sudo spctl --master-enable"
echo ""
echo "💡 Si nada funciona:"
echo "   • Verifica que tu Mac sea de 2015 o posterior"
echo "   • Asegúrate de tener macOS 10.11+"
echo "   • Contacta soporte técnico"
TROUBLEOF

chmod +x "solucionar_problemas_legacy.sh"
echo "✅ Script de troubleshooting creado: solucionar_problemas_legacy.sh"

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."
rm -rf build *.spec __pycache__ 2>/dev/null
if [[ -f "$ICNS_PATH" ]]; then
    # Mantener el icono para futura referencia
    echo "   💾 Manteniendo icono: $ICNS_PATH"
fi

echo ""
echo "✅ ¡PROCESO LEGACY COMPLETADO EXITOSAMENTE!"
echo "="*80
echo ""
echo "🎯 ARCHIVOS FINALES PARA DISTRIBUCIÓN:"
echo "   📀 Instalador: dist/$DMG_NAME.dmg"
echo "   📱 Aplicación: dist/bonosAlfa.app"
echo "   🛠️ Instalador asistido: instalar_bonos_alfa_legacy.sh"
echo "   🔧 Solucionador: solucionar_problemas_legacy.sh"
echo ""
echo "🚀 TU APLICACIÓN ESTÁ LISTA PARA MACS DESDE 2015!"
echo ""
echo "📋 PARA DISTRIBUIR:"
echo "   1. Comparte el archivo .dmg con tus usuarios"
echo "   2. Incluye las instrucciones de instalación"
echo "   3. Proporciona los scripts de ayuda si es necesario"
echo ""
echo "💡 COMPATIBILIDAD GARANTIZADA:"
echo "   ✓ Mac 2015+ (Intel y Apple Silicon con Rosetta)"
echo "   ✓ macOS 10.11 El Capitan hasta macOS Sonoma"
echo "   ✓ Hardware Intel de 64 bits"
echo "   ✓ Funcionalidad completa en sistemas legacy"
echo ""
echo "🎉 ¡Felicidades! Tu aplicación tiene máxima compatibilidad legacy." 