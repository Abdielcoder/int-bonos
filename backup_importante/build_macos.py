#!/usr/bin/env python3
"""
Script específico para crear ejecutable en macOS
Usa solo PySide6 para evitar conflictos con PyQt6
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("🔧 Instalando dependencias...")
    
    # Desinstalar PyQt6 si está presente para evitar conflictos
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "PyQt6", "-y"], 
                      capture_output=True, text=True)
        print("✅ PyQt6 desinstalado para evitar conflictos")
    except:
        pass
    
    # Instalar PySide6
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "PySide6"], check=True)
        print("✅ PySide6 instalado")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar PySide6")
        return False
    
    # Instalar PyInstaller
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller instalado")
    except subprocess.CalledProcessError:
        print("❌ Error al instalar PyInstaller")
        return False
    
    # Instalar otras dependencias
    dependencies = ["requests", "pandas", "openpyxl", "xlsxwriter"]
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"✅ {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"⚠️ Error al instalar {dep}")
    
    return True

def create_spec_file():
    """Crea un archivo .spec optimizado para macOS"""
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
    [],
    exclude_binaries=True,
    name='HerramientasBonos',
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
    name='HerramientasBonos',
)

# Crear bundle .app para macOS
app = BUNDLE(
    coll,
    name='HerramientasBonos.app',
    icon=None,
    bundle_identifier='com.rinorisk.herramientasbonos',
    version='2.0.0',
    info_plist={
        'CFBundleName': 'Herramientas Bonos',
        'CFBundleDisplayName': 'Herramientas Bonos',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15.0',
    },
)
'''
    
    with open("herramientas_bonos_macos.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado para macOS")

def build_executable():
    """Construye el ejecutable usando el archivo .spec"""
    print("🔨 Construyendo ejecutable para macOS...")
    
    try:
        # Limpiar builds anteriores
        for path in ["build", "dist", "__pycache__"]:
            if Path(path).exists():
                import shutil
                shutil.rmtree(path)
        
        # Eliminar archivos .spec anteriores
        for spec_file in Path(".").glob("*.spec"):
            if spec_file.name != "herramientas_bonos_macos.spec":
                spec_file.unlink()
        
        # Construir usando el archivo .spec
        result = subprocess.run([
            "pyinstaller", 
            "herramientas_bonos_macos.spec",
            "--clean",
            "--noconfirm"
        ], check=True, capture_output=True, text=True)
        
        # Verificar que se creó el .app
        app_path = Path("dist/HerramientasBonos.app")
        if app_path.exists():
            print(f"✅ ¡Ejecutable creado exitosamente!")
            print(f"📁 Ubicación: {app_path.absolute()}")
            
            # Mostrar tamaño
            size_mb = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file()) / (1024 * 1024)
            print(f"📊 Tamaño: {size_mb:.1f} MB")
            
            return True
        else:
            print("❌ El ejecutable no se creó correctamente")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir el ejecutable:")
        print(f"   Código de salida: {e.returncode}")
        if e.stdout:
            print(f"   Salida: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def main():
    print("🚀 Iniciando construcción para macOS")
    print("=" * 50)
    
    # Verificar que estamos en macOS
    if platform.system() != "Darwin":
        print("❌ Este script solo funciona en macOS")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    # Crear archivo .spec
    create_spec_file()
    
    # Construir ejecutable
    if build_executable():
        print("\n🎉 ¡Proceso completado exitosamente!")
        print("\n📋 Instrucciones:")
        print("   • El ejecutable está en: dist/HerramientasBonos.app")
        print("   • Puedes ejecutarlo haciendo doble clic")
        print("   • Para distribuir, comprime la carpeta .app")
    else:
        print("\n❌ El proceso falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 