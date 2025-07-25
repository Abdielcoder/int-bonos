@echo off
REM Script para crear ejecutable bonosAlfa.exe en Windows
REM Uso: crear_bonos_alfa_windows.bat

echo 🚀 Iniciando creación de ejecutable bonosAlfa para WINDOWS
echo 📱 Versión: 1.0.0
echo 💻 Sistema: Windows

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no está instalado o no está en PATH
    echo    Descarga Python desde: https://python.org
    pause
    exit /b 1
)
echo ✅ Python detectado

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no está disponible
    pause
    exit /b 1
)
echo ✅ pip disponible

REM Instalar dependencias necesarias
echo 🔍 Verificando e instalando dependencias...

echo   📦 Instalando PyInstaller...
pip install pyinstaller

echo   📦 Instalando PySide6...
pip install PySide6

echo   📦 Instalando pandas...
pip install pandas

echo   📦 Instalando requests...
pip install requests

echo   📦 Instalando openpyxl...
pip install openpyxl

echo   📦 Instalando xlsxwriter...
pip install xlsxwriter

echo   📦 Instalando Pillow...
pip install Pillow

REM Limpiar builds anteriores
echo 🧹 Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Crear archivo spec para Windows
echo 🏗️ Creando configuración para Windows...

(
echo # -*- mode: python ; coding: utf-8 -*-
echo # Configuración para bonosAlfa Windows
echo.
echo block_cipher = None
echo.
echo # Lista completa de imports ocultos
echo hidden_imports = [
echo     # Encodings críticos
echo     'encodings',
echo     'encodings.utf_8',
echo     'encodings.ascii',
echo     'encodings.latin_1',
echo     'encodings.cp1252',
echo     'encodings.idna',
echo     'encodings.aliases',
echo.    
echo     # Framework Qt - PySide6
echo     'PySide6',
echo     'PySide6.QtCore',
echo     'PySide6.QtGui',
echo     'PySide6.QtWidgets',
echo     'PySide6.QtNetwork',
echo     'shiboken6',
echo.    
echo     # Data processing
echo     'pandas',
echo     'pandas.core',
echo     'pandas.io',
echo     'pandas.io.excel',
echo     'numpy',
echo.    
echo     # File handling
echo     'openpyxl',
echo     'xlsxwriter',
echo.    
echo     # Network
echo     'requests',
echo     'urllib3',
echo     'certifi',
echo     'ssl',
echo.    
echo     # Standard library
echo     'json',
echo     'pathlib',
echo     'datetime',
echo     'csv',
echo     'tempfile',
echo     'os',
echo     'sys',
echo ]
echo.
echo a = Analysis^(
echo     ['main.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('principal.py', '.'^),
echo         ^('assets', 'assets'^),
echo     ],
echo     hiddenimports=hidden_imports,
echo     hookspath=[],
echo     runtime_hooks=[],
echo     excludes=[
echo         'tkinter',
echo         'matplotlib',
echo         'PyQt6',
echo         'PyQt5',
echo         'PySide2',
echo     ],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='bonosAlfa',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     icon='assets\\img\\logo.ico' if os.path.exists^('assets\\img\\logo.ico'^) else None,
echo ^)
) > bonosAlfa_windows.spec

REM Construir el ejecutable
echo 🔨 Construyendo bonosAlfa.exe...
pyinstaller --clean --noconfirm bonosAlfa_windows.spec

REM Verificar resultado
if exist "dist\bonosAlfa.exe" (
    echo ✅ ¡bonosAlfa.exe creado exitosamente!
    echo 📁 Ubicación: dist\bonosAlfa.exe
    
    REM Mostrar tamaño
    for %%I in ("dist\bonosAlfa.exe") do echo 📊 Tamaño: %%~zI bytes
    
    echo.
    echo 📋 INSTRUCCIONES DE USO:
    echo ========================================
    echo 🪟 Para usar en Windows:
    echo    1. Ejecuta dist\bonosAlfa.exe
    echo    2. Copia el archivo donde desees
    echo    3. Crea acceso directo si quieres
    echo.
    echo ✅ Dependencias incluidas:
    echo    • PySide6 ^(UI framework^)
    echo    • pandas ^(procesamiento datos^)
    echo    • requests ^(HTTP client^)
    echo    • openpyxl, xlsxwriter ^(Excel^)
    echo    • Todas las dependencias del sistema
    
) else (
    echo ❌ Error: No se pudo crear bonosAlfa.exe
    echo    Revisa los errores anteriores
)

REM Limpiar archivos temporales
echo.
echo 🧹 Limpiando archivos temporales...
if exist build rmdir /s /q build
if exist *.spec del *.spec

echo.
echo ✅ ¡Proceso completado!
pause 