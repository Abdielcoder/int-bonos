# Script PowerShell para crear ejecutable bonosAlfa.exe en Windows
# Uso: .\crear_bonos_alfa_windows.ps1

param(
    [switch]$SkipDependencies = $false
)

Write-Host "🚀 Iniciando creación de ejecutable bonosAlfa para WINDOWS" -ForegroundColor Green
Write-Host "📱 Versión: 1.0.0" -ForegroundColor Cyan
Write-Host "💻 Sistema: Windows" -ForegroundColor Cyan

# Verificar Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "   Descarga Python desde: https://python.org" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Verificar pip
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip disponible: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ pip no está disponible" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}

# Instalar dependencias
if (-not $SkipDependencies) {
    Write-Host "🔍 Verificando e instalando dependencias..." -ForegroundColor Yellow
    
    $dependencies = @(
        "pyinstaller",
        "PySide6", 
        "pandas",
        "requests",
        "openpyxl",
        "xlsxwriter",
        "Pillow"
    )
    
    foreach ($dep in $dependencies) {
        Write-Host "  📦 Instalando $dep..." -ForegroundColor Cyan
        pip install $dep --quiet
    }
    
    Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
}

# Limpiar builds anteriores
Write-Host "🧹 Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
Get-ChildItem "*.spec" | Remove-Item -Force

# Crear archivo spec para Windows
Write-Host "🏗️ Creando configuración para Windows..." -ForegroundColor Yellow

$specContent = @"
# -*- mode: python ; coding: utf-8 -*-
# Configuración para bonosAlfa Windows

import os

block_cipher = None

# Lista completa de imports ocultos
hidden_imports = [
    # Encodings críticos
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
    
    # Módulos estándar críticos
    'zipimport',
    'importlib',
    'importlib.util',
    'collections',
    'functools',
    'itertools',
    'copy',
    'pickle',
    
    # Data processing
    'pandas',
    'pandas.core',
    'pandas.core.arrays',
    'pandas.io',
    'pandas.io.formats',
    'pandas.io.excel',
    'numpy',
    'numpy.core',
    
    # File handling
    'openpyxl',
    'openpyxl.workbook',
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
    
    # Text processing
    'charset_normalizer',
    'idna',
    're',
    'string',
    
    # Date and time
    'datetime',
    'dateutil',
    'pytz',
    'time',
    
    # Standard library
    'json',
    'pathlib',
    'typing',
    'base64',
    'hashlib',
    'os',
    'sys',
    'tempfile',
    'csv',
    'io',
    'math',
    'platform',
    'subprocess',
    'threading',
]

# Archivos de datos
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
        'PyQt6',
        'PyQt5',
        'PySide2',
        'unittest',
        'test',
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
    name='bonosAlfa',
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
    icon='assets/img/logo.ico' if os.path.exists('assets/img/logo.ico') else None,
)
"@

$specContent | Out-File -FilePath "bonosAlfa_windows.spec" -Encoding UTF8

# Construir el ejecutable
Write-Host "🔨 Construyendo bonosAlfa.exe..." -ForegroundColor Yellow
try {
    pyinstaller --clean --noconfirm "bonosAlfa_windows.spec"
    
    if (Test-Path "dist\bonosAlfa.exe") {
        Write-Host "✅ ¡bonosAlfa.exe creado exitosamente!" -ForegroundColor Green
        
        $exePath = Get-Item "dist\bonosAlfa.exe"
        $sizeInMB = [math]::Round($exePath.Length / 1MB, 1)
        
        Write-Host "📁 Ubicación: $($exePath.FullName)" -ForegroundColor Cyan
        Write-Host "📊 Tamaño: $sizeInMB MB" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "📋 INSTRUCCIONES DE USO:" -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "🪟 Para usar en Windows:" -ForegroundColor White
        Write-Host "   1. Ejecuta dist\bonosAlfa.exe" -ForegroundColor Gray
        Write-Host "   2. Copia el archivo donde desees" -ForegroundColor Gray
        Write-Host "   3. Crea acceso directo si quieres" -ForegroundColor Gray
        Write-Host ""
        Write-Host "✅ Dependencias incluidas:" -ForegroundColor Green
        Write-Host "   • PySide6 (UI framework)" -ForegroundColor Gray
        Write-Host "   • pandas (procesamiento datos)" -ForegroundColor Gray
        Write-Host "   • requests (HTTP client)" -ForegroundColor Gray
        Write-Host "   • openpyxl, xlsxwriter (Excel)" -ForegroundColor Gray
        Write-Host "   • Todas las dependencias del sistema" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Error: No se pudo crear bonosAlfa.exe" -ForegroundColor Red
        Write-Host "   Revisa los errores anteriores" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error durante la construcción: $_" -ForegroundColor Red
}

# Limpiar archivos temporales
Write-Host ""
Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Get-ChildItem "*.spec" | Remove-Item -Force

Write-Host ""
Write-Host "✅ ¡Proceso completado!" -ForegroundColor Green
Read-Host "Presiona Enter para continuar" 