#!/usr/bin/env python3
"""
Script específico para crear ejecutable en Windows
Usa solo PySide6 para evitar conflictos con PyQt6
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("[INSTALL] Instalando dependencias...")
    
    # Desinstalar PyQt6 si está presente para evitar conflictos
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "PyQt6", "-y"], 
                      capture_output=True, text=True)
        print("[OK] PyQt6 desinstalado para evitar conflictos")
    except:
        pass
    
    # Instalar PySide6
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "PySide6"], check=True)
        print("[OK] PySide6 instalado")
    except subprocess.CalledProcessError:
        print("[ERROR] Error al instalar PySide6")
        return False
    
    # Instalar PyInstaller
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("[OK] PyInstaller instalado")
    except subprocess.CalledProcessError:
        print("[ERROR] Error al instalar PyInstaller")
        return False
    
    # Instalar otras dependencias
    dependencies = ["requests", "pandas", "openpyxl", "xlsxwriter"]
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            print(f"[OK] {dep} instalado")
        except subprocess.CalledProcessError:
            print(f"[WARNING] Error al instalar {dep}")
    
    return True

def create_spec_file():
    """Crea un archivo .spec optimizado para Windows"""
    
    # Lista de archivos que siempre deben incluirse
    required_files = [
        ('principal.py', '.'),
        ('assets', 'assets'),
        ('otp_dialog.py', '.'),
        ('otp_service.py', '.'),
        ('resegmentacion_db.py', '.'),
        ('resegmentacion_details_dialog.py', '.'),
    ]
    
    # Agregar archivos opcionales solo si existen
    optional_files = [
        ('resegmentaciones.db', '.'),
    ]
    
    # Filtrar archivos que existen
    datas_files = required_files.copy()
    for file_path, dest in optional_files:
        if Path(file_path).exists():
            datas_files.append((file_path, dest))
            print(f"[INFO] Incluyendo archivo opcional: {file_path}")
        else:
            print(f"[WARNING] Archivo no encontrado, omitiendo: {file_path}")
    
    # Crear la lista de datos como string
    datas_str = ',\n        '.join([f"('{file_path}', '{dest}')" for file_path, dest in datas_files])
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ''' + datas_str + ''',
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
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open("herramientas_bonos_windows.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("[OK] Archivo .spec creado para Windows")

def build_executable():
    """Construye el ejecutable usando el archivo .spec"""
    print("[BUILD] Construyendo ejecutable para Windows...")
    
    try:
        # Limpiar builds anteriores
        for path in ["build", "dist", "__pycache__"]:
            if Path(path).exists():
                import shutil
                shutil.rmtree(path)
        
        # Eliminar archivos .spec anteriores
        for spec_file in Path(".").glob("*.spec"):
            if spec_file.name != "herramientas_bonos_windows.spec":
                spec_file.unlink()
        
        # Construir usando el archivo .spec
        result = subprocess.run([
            "pyinstaller", 
            "herramientas_bonos_windows.spec",
            "--clean",
            "--noconfirm"
        ], check=True, capture_output=True, text=True)
        
        # Verificar que se creó el .exe
        exe_path = Path("dist/HerramientasBonos.exe")
        if exe_path.exists():
            print(f"[OK] ¡Ejecutable creado exitosamente!")
            print(f"[INFO] Ubicación: {exe_path.absolute()}")
            
            # Mostrar tamaño
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"[INFO] Tamaño: {size_mb:.1f} MB")
            
            return True
        else:
            print("[ERROR] El ejecutable no se creó correctamente")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error al construir el ejecutable:")
        print(f"   Código de salida: {e.returncode}")
        if e.stdout:
            print(f"   Salida: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def main():
    print("[START] Iniciando construcción para Windows")
    print("=" * 50)
    
    # Verificar que estamos en Windows
    if platform.system() != "Windows":
        print("[ERROR] Este script solo funciona en Windows")
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    # Crear archivo .spec
    create_spec_file()
    
    # Construir ejecutable
    if build_executable():
        print("\n[SUCCESS] ¡Proceso completado exitosamente!")
        print("\n[INFO] Instrucciones:")
        print("   • El ejecutable está en: dist/HerramientasBonos.exe")
        print("   • Puedes ejecutarlo haciendo doble clic")
        print("   • Para distribuir, comparte el archivo .exe")
        print("   • No requiere instalación de Python en el sistema destino")
    else:
        print("\n[ERROR] El proceso falló")
        sys.exit(1)

if __name__ == "__main__":
    main() 