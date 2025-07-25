#!/usr/bin/env python3
"""
Script especializado para crear el ejecutable bonosAlfa
Configurado específicamente para la distribución e instalación
"""

import subprocess
import sys
import platform
import os
from pathlib import Path
import shutil

def verificar_pyinstaller():
    """Verifica e instala PyInstaller si es necesario"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
        return True
    except ImportError:
        print("🔧 Instalando PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller instalado exitosamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error al instalar PyInstaller")
            return False

def detectar_qt():
    """Detecta el framework Qt disponible"""
    try:
        import PyQt6
        print("✅ Detectado PyQt6")
        return "PyQt6"
    except ImportError:
        try:
            import PySide6
            print("✅ Detectado PySide6")
            return "PySide6"
        except ImportError:
            print("❌ No se encontró PyQt6 ni PySide6")
            return None

def crear_spec_bonos_alfa():
    """Crea el archivo .spec personalizado para bonosAlfa"""
    
    qt_framework = detectar_qt()
    if not qt_framework:
        return False
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Archivo de configuración para bonosAlfa

block_cipher = None

# Framework Qt detectado: {qt_framework}
QT_FRAMEWORK = "{qt_framework}"

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('principal.py', '.'),
        ('otp_dialog.py', '.'),
        ('otp_service.py', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        QT_FRAMEWORK,
        f'{{QT_FRAMEWORK}}.QtCore',
        f'{{QT_FRAMEWORK}}.QtGui',
        f'{{QT_FRAMEWORK}}.QtWidgets',
        'requests',
        'pandas',
        'openpyxl',
        'xlsxwriter',
        'json',
        'csv',
        'tempfile',
        'datetime',
        'pathlib',
        'urllib3',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.distutils',
        'tkinter',
        'unittest',
        'test',
        'pydoc_data',
        'PyQt5' if QT_FRAMEWORK != 'PyQt5' else '',
        'PySide2' if QT_FRAMEWORK != 'PySide2' else '',
        'PyQt6' if QT_FRAMEWORK != 'PyQt6' else '',
        'PySide6' if QT_FRAMEWORK != 'PySide6' else '',
        'nicegui',
        'fastapi',
        'uvicorn',
        'django',
        'flask',
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
)

# Para macOS, crear bundle .app
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='bonosAlfa.app',
        icon='assets/img/logo.png' if os.path.exists('assets/img/logo.png') else None,
        bundle_identifier='com.rinorisk.bonos.alfa',
        version='1.0.0',
        info_plist={{
            'CFBundleName': 'Bonos Alfa',
            'CFBundleDisplayName': 'Bonos Alfa',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.15.0',
            'CFBundleDocumentTypes': [
                {{
                    'CFBundleTypeName': 'Excel Files',
                    'CFBundleTypeExtensions': ['xlsx', 'xls'],
                    'CFBundleTypeRole': 'Editor'
                }}
            ]
        }},
    )
'''
    
    with open("bonosAlfa.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo bonosAlfa.spec creado")
    return True

def construir_bonos_alfa():
    """Construye el ejecutable bonosAlfa"""
    
    sistema = platform.system()
    print(f"🖥️  Construyendo bonosAlfa para: {sistema}")
    
    # Verificar archivos necesarios
    archivos_necesarios = ["main.py", "principal.py"]
    for archivo in archivos_necesarios:
        if not Path(archivo).exists():
            print(f"❌ Error: No se encontró {archivo}")
            return False
    
    # Crear el archivo .spec
    if not crear_spec_bonos_alfa():
        return False
    
    # Comando de construcción usando el archivo .spec
    comando = [
        "pyinstaller",
        "--clean",
        "--noconfirm",
        "bonosAlfa.spec"
    ]
    
    print("🔨 Construyendo ejecutable bonosAlfa...")
    print(f"📋 Comando: {' '.join(comando)}")
    
    try:
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        
        # Verificar que se creó el ejecutable
        if sistema == "Darwin":  # macOS
            ejecutable_app = Path("dist/bonosAlfa.app")
            ejecutable_bin = Path("dist/bonosAlfa")
            
            if ejecutable_app.exists():
                print(f"✅ ¡bonosAlfa.app creado exitosamente!")
                print(f"📁 Ubicación: {ejecutable_app.absolute()}")
                return True
            elif ejecutable_bin.exists():
                print(f"✅ ¡bonosAlfa creado exitosamente!")
                print(f"📁 Ubicación: {ejecutable_bin.absolute()}")
                return True
        
        elif sistema == "Windows":
            ejecutable = Path("dist/bonosAlfa.exe")
            if ejecutable.exists():
                print(f"✅ ¡bonosAlfa.exe creado exitosamente!")
                print(f"📁 Ubicación: {ejecutable.absolute()}")
                return True
        
        else:  # Linux
            ejecutable = Path("dist/bonosAlfa")
            if ejecutable.exists():
                print(f"✅ ¡bonosAlfa creado exitosamente!")
                print(f"📁 Ubicación: {ejecutable.absolute()}")
                # Hacer ejecutable en Linux
                os.chmod(ejecutable, 0o755)
                return True
        
        print("❌ No se encontró el ejecutable generado")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al construir bonosAlfa:")
        print(f"   Código de salida: {e.returncode}")
        if e.stdout:
            print(f"   Salida: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def crear_instalador_macos():
    """Crea un instalador DMG para macOS"""
    sistema = platform.system()
    if sistema != "Darwin":
        print("ℹ️  Instalador DMG solo disponible en macOS")
        return False
    
    app_path = Path("dist/bonosAlfa.app")
    if not app_path.exists():
        print("❌ No se encontró bonosAlfa.app")
        return False
    
    print("📦 Creando instalador DMG...")
    
    # Comando para crear DMG
    dmg_name = "bonosAlfa-installer.dmg"
    comando_dmg = [
        "hdiutil", "create", 
        "-volname", "Bonos Alfa Installer",
        "-srcfolder", "dist/bonosAlfa.app",
        "-ov", "-format", "UDZO",
        f"dist/{dmg_name}"
    ]
    
    try:
        subprocess.run(comando_dmg, check=True)
        print(f"✅ Instalador DMG creado: dist/{dmg_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando DMG: {e}")
        return False

def limpiar_archivos_construccion():
    """Limpia archivos temporales de la construcción"""
    print("🧹 Limpiando archivos temporales...")
    
    carpetas_limpiar = ["build", "__pycache__"]
    archivos_limpiar = ["bonosAlfa.spec"]
    
    for carpeta in carpetas_limpiar:
        if Path(carpeta).exists():
            try:
                shutil.rmtree(carpeta)
                print(f"   ✅ Eliminada: {carpeta}")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {carpeta}: {e}")
    
    for archivo in archivos_limpiar:
        archivo_path = Path(archivo)
        if archivo_path.exists():
            try:
                archivo_path.unlink()
                print(f"   ✅ Eliminado: {archivo}")
            except Exception as e:
                print(f"   ⚠️  Error eliminando {archivo}: {e}")

def mostrar_instrucciones_instalacion():
    """Muestra las instrucciones de instalación según el sistema"""
    sistema = platform.system()
    
    print("\n" + "="*60)
    print("📋 INSTRUCCIONES DE INSTALACIÓN")
    print("="*60)
    
    if sistema == "Darwin":  # macOS
        print("🍎 macOS:")
        print("   1. Busca el archivo bonosAlfa.app en la carpeta dist/")
        print("   2. Arrastra bonosAlfa.app a la carpeta Aplicaciones")
        print("   3. Ejecuta desde Launchpad o Finder")
        print("   4. Si aparece advertencia de seguridad:")
        print("      - Ve a Preferencias > Seguridad y Privacidad")
        print("      - Haz clic en 'Abrir de todas formas'")
        
        if Path("dist/bonosAlfa-installer.dmg").exists():
            print("\n   📦 También tienes disponible el instalador DMG:")
            print("      - Doble clic en bonosAlfa-installer.dmg")
            print("      - Arrastra la aplicación a Aplicaciones")
    
    elif sistema == "Windows":
        print("🪟 Windows:")
        print("   1. Busca el archivo bonosAlfa.exe en la carpeta dist\\")
        print("   2. Copia bonosAlfa.exe donde desees instalarlo")
        print("   3. Crea un acceso directo en el Escritorio si quieres")
        print("   4. Ejecuta con doble clic")
    
    else:  # Linux
        print("🐧 Linux:")
        print("   1. Busca el archivo bonosAlfa en la carpeta dist/")
        print("   2. Copia a /usr/local/bin/ para instalación global:")
        print("      sudo cp dist/bonosAlfa /usr/local/bin/")
        print("   3. O ejecuta directamente: ./dist/bonosAlfa")
    
    print("\n✅ El ejecutable incluye todas las dependencias necesarias")
    print("✅ No requiere instalación de Python en el sistema destino")

def main():
    """Función principal"""
    print("🚀 GENERADOR DEL EJECUTABLE BONOS ALFA")
    print("="*50)
    
    # Verificar PyInstaller
    if not verificar_pyinstaller():
        sys.exit(1)
    
    # Verificar framework Qt
    if not detectar_qt():
        print("❌ Instala PyQt6 o PySide6:")
        print("   pip install PyQt6")
        print("   o")
        print("   pip install PySide6")
        sys.exit(1)
    
    # Construir el ejecutable
    if construir_bonos_alfa():
        print("\n✅ ¡bonosAlfa construido exitosamente!")
        
        # Crear instalador DMG en macOS
        if platform.system() == "Darwin":
            crear_instalador_macos()
        
        # Mostrar instrucciones
        mostrar_instrucciones_instalacion()
        
        # Preguntar sobre limpieza
        try:
            respuesta = input("\n¿Limpiar archivos temporales? (s/n): ")
            if respuesta.lower() in ['s', 'sí', 'si', 'y', 'yes']:
                limpiar_archivos_construccion()
        except KeyboardInterrupt:
            print("\n\n👋 Proceso completado")
        
        print(f"\n🎉 ¡bonosAlfa está listo para distribución!")
        
    else:
        print("\n❌ Error en la construcción del ejecutable")
        sys.exit(1)

if __name__ == "__main__":
    main() 