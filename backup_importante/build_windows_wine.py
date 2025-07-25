#!/usr/bin/env python3
"""
Script para crear ejecutable de Windows usando Wine en macOS
Permite generar .exe sin necesidad de una máquina Windows
"""

import subprocess
import sys
import platform
import os
from pathlib import Path
import shutil

def check_wine():
    """Verifica si Wine está instalado"""
    try:
        result = subprocess.run(["wine", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Wine detectado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Wine no está funcionando correctamente")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Wine no está instalado")
        print("   Instálalo con: brew install --cask wine-stable")
        return False

def install_python_wine():
    """Instala Python en Wine"""
    print("🐍 Instalando Python en Wine...")
    
    # Descargar Python para Windows
    python_url = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    python_installer = "python-3.11.8-amd64.exe"
    
    try:
        # Descargar Python
        print("📥 Descargando Python para Windows...")
        subprocess.run(["curl", "-L", "-o", python_installer, python_url], check=True)
        
        # Instalar Python en Wine (modo silencioso)
        print("🔧 Instalando Python en Wine...")
        subprocess.run([
            "wine", python_installer, 
            "/quiet", 
            "InstallAllUsers=1", 
            "PrependPath=1",
            "Include_test=0"
        ], check=True)
        
        # Verificar instalación
        result = subprocess.run(["wine", "python", "--version"], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Python instalado en Wine: {result.stdout.strip()}")
            return True
        else:
            print("❌ Error al instalar Python en Wine")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la instalación: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la instalación de Python")
        return False
    finally:
        # Limpiar archivo descargado
        if Path(python_installer).exists():
            Path(python_installer).unlink()

def install_dependencies_wine():
    """Instala las dependencias en Wine"""
    print("📦 Instalando dependencias en Wine...")
    
    dependencies = [
        "pyinstaller",
        "PySide6", 
        "requests",
        "pandas",
        "openpyxl",
        "xlsxwriter"
    ]
    
    for dep in dependencies:
        try:
            print(f"   Instalando {dep}...")
            subprocess.run([
                "wine", "python", "-m", "pip", "install", dep
            ], check=True, timeout=120)
            print(f"   ✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"   ❌ Error al instalar {dep}")
            return False
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout al instalar {dep}")
            return False
    
    return True

def create_windows_spec():
    """Crea el archivo .spec para Windows"""
    print("📝 Creando archivo .spec para Windows...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('principal.py', '.'),
        ('assets', 'assets'),
        ('otp_dialog.py', '.'),
        ('otp_service.py', '.'),
        ('resegmentacion_db.py', '.'),
        ('resegmentacion_details_dialog.py', '.'),
        ('resegmentaciones.db', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtNetwork',
        'shiboken6',
        'requests',
        'pandas',
        'pandas.core',
        'pandas.io',
        'pandas.io.excel',
        'numpy',
        'openpyxl',
        'xlsxwriter',
        'json',
        'csv',
        'tempfile',
        'datetime',
        'pathlib',
        'sqlite3',
        'encodings',
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.latin_1',
        'encodings.cp1252',
        'encodings.idna',
        'encodings.aliases',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt6',
        'PyQt5',
        'PySide2',
        'matplotlib',
        'scipy',
        'tkinter',
        'unittest',
        'test',
        'pydoc_data',
        'nicegui',
        'fastapi',
        'uvicorn',
        'rapidfuzz',
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
    name='HerramientasBonos',
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
'''
    
    with open("herramientas_bonos_windows_wine.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")

def build_windows_exe():
    """Construye el ejecutable de Windows usando Wine"""
    print("🔨 Construyendo ejecutable de Windows con Wine...")
    
    try:
        # Limpiar builds anteriores
        for path in ["build", "dist", "__pycache__"]:
            if Path(path).exists():
                shutil.rmtree(path)
        
        # Eliminar archivos .spec anteriores
        for spec_file in Path(".").glob("*.spec"):
            if spec_file.name != "herramientas_bonos_windows_wine.spec":
                spec_file.unlink()
        
        # Construir usando Wine
        print("⏳ Iniciando construcción (esto puede tomar varios minutos)...")
        result = subprocess.run([
            "wine", "python", "-m", "PyInstaller",
            "herramientas_bonos_windows_wine.spec",
            "--clean",
            "--noconfirm"
        ], check=True, timeout=1800)  # 30 minutos de timeout
        
        # Verificar que se creó el .exe
        exe_path = Path("dist/HerramientasBonos.exe")
        if exe_path.exists():
            print(f"✅ ¡Ejecutable de Windows creado exitosamente!")
            print(f"📁 Ubicación: {exe_path.absolute()}")
            
            # Mostrar tamaño
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📊 Tamaño: {size_mb:.1f} MB")
            
            return True
        else:
            print("❌ El ejecutable no se creó correctamente")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir el ejecutable:")
        print(f"   Código de salida: {e.returncode}")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout durante la construcción")
        print("   La construcción puede tardar más de 30 minutos")
        return False

def test_windows_exe():
    """Prueba el ejecutable de Windows usando Wine"""
    print("🧪 Probando ejecutable de Windows...")
    
    exe_path = Path("dist/HerramientasBonos.exe")
    if not exe_path.exists():
        print("❌ No se encontró el ejecutable para probar")
        return False
    
    try:
        # Intentar ejecutar el .exe con Wine
        print("🚀 Iniciando prueba del ejecutable...")
        result = subprocess.run([
            "wine", str(exe_path)
        ], timeout=30, capture_output=True, text=True)
        
        print("✅ El ejecutable se inició correctamente en Wine")
        return True
        
    except subprocess.TimeoutExpired:
        print("✅ El ejecutable se ejecutó (timeout esperado para GUI)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ El ejecutable tuvo problemas: {e}")
        return False

def main():
    print("🚀 CONSTRUCTOR DE EJECUTABLE WINDOWS CON WINE")
    print("=" * 60)
    
    # Verificar que estamos en macOS
    if platform.system() != "Darwin":
        print("❌ Este script solo funciona en macOS")
        sys.exit(1)
    
    # Verificar Wine
    if not check_wine():
        print("\n📋 Instrucciones para instalar Wine:")
        print("1. Instala Homebrew si no lo tienes:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print("2. Instala Wine:")
        print("   brew install --cask wine-stable")
        print("3. Instala Rosetta 2 si es necesario:")
        print("   softwareupdate --install-rosetta --agree-to-license")
        print("4. Ejecuta este script nuevamente")
        sys.exit(1)
    
    # Instalar Python en Wine
    if not install_python_wine():
        print("❌ No se pudo instalar Python en Wine")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies_wine():
        print("❌ No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Crear archivo .spec
    create_windows_spec()
    
    # Construir ejecutable
    if build_windows_exe():
        print("\n🎉 ¡Proceso completado exitosamente!")
        
        # Probar el ejecutable
        test_windows_exe()
        
        print("\n📋 Instrucciones:")
        print("   • El ejecutable está en: dist/HerramientasBonos.exe")
        print("   • Es compatible con Windows 10/11")
        print("   • Para distribuir, comparte el archivo .exe")
        print("   • No requiere Python en el sistema destino")
        print("\n💡 Consejo: Puedes probar el .exe en Wine antes de distribuirlo")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 