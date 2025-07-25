#!/usr/bin/env python3
"""
Script automatizado para crear ejecutable de Herramientas Bonos con PyQt/PySide
Detecta automáticamente el sistema operativo y las dependencias Qt disponibles
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def install_pyinstaller():
    """Instala PyInstaller si no está disponible"""
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

def detect_qt_framework():
    """Detecta qué framework Qt está disponible"""
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

def build_executable():
    """Construye el ejecutable usando PyInstaller para PyQt/PySide"""
    
    # Detectar el sistema operativo
    sistema = platform.system()
    print(f"🖥️  Construyendo para: {sistema}")
    
    # Detectar framework Qt
    qt_framework = detect_qt_framework()
    if not qt_framework:
        print("❌ Error: No se encontró PyQt6 ni PySide6")
        print("   Instala uno de ellos con:")
        print("   pip install PyQt6  o  pip install PySide6")
        return False
    
    # Archivos y carpetas a incluir
    assets_path = Path("assets")
    data_files = []
    
    if assets_path.exists():
        # Incluir toda la carpeta assets
        data_files.append(f"--add-data=assets{os.pathsep}assets")
        print(f"✅ Incluyendo carpeta assets")
    
    # Incluir principal.py
    if Path("principal.py").exists():
        data_files.append(f"--add-data=principal.py{os.pathsep}.")
        print(f"✅ Incluyendo principal.py")
    
    # Comando base de PyInstaller
    comando = [
        "pyinstaller",
        "--onefile",                           # Un solo archivo ejecutable
        "--windowed",                          # Sin consola (GUI)
        "--name=HerramientasBonos",            # Nombre del ejecutable
        "--clean",                             # Limpiar cache anterior
        "--noconfirm",                         # No pedir confirmación
    ]
    
    # Agregar datos
    comando.extend(data_files)
    
    # Hidden imports específicos para PyQt/PySide
    hidden_imports = [
        qt_framework,
        f"{qt_framework}.QtCore",
        f"{qt_framework}.QtGui", 
        f"{qt_framework}.QtWidgets",
        "requests",
        "pandas",
        "json",
        "csv",
        "tempfile",
        "datetime",
        "pathlib"
    ]
    
    for import_name in hidden_imports:
        comando.extend(["--hidden-import", import_name])
    
    # Excluir módulos innecesarios para reducir tamaño
    exclude_modules = [
        "matplotlib",
        "scipy",
        "numpy.distutils",
        "tkinter",
        "unittest",
        "test",
        "pydoc_data",
        "PyQt5",
        "PySide2",
        "nicegui",  # Excluir NiceGUI explícitamente
        "fastapi",
        "uvicorn"
    ]
    
    for module in exclude_modules:
        comando.extend(["--exclude-module", module])
    
    # Configurar icono según el sistema
    icon_path = None
    if sistema == "Windows":
        if Path("assets/img/icon.ico").exists():
            icon_path = "assets/img/icon.ico"
        comando.append("--console")  # Temporalmente para debug
    elif sistema == "Darwin":  # macOS
        if Path("assets/img/icon.icns").exists():
            icon_path = "assets/img/icon.icns"
    else:  # Linux
        if Path("assets/img/icon.png").exists():
            icon_path = "assets/img/icon.png"
    
    if icon_path:
        comando.extend(["--icon", icon_path])
        print(f"✅ Usando icono: {icon_path}")
    
    # Archivo principal
    comando.append("main.py")
    
    print("🔨 Comando de construcción:")
    print(" ".join(comando))
    
    # Ejecutar PyInstaller
    try:
        print("🔨 Construyendo ejecutable...")
        resultado = subprocess.run(comando, check=True, capture_output=True, text=True)
        
        # Mostrar ubicación del ejecutable
        if sistema == "Windows":
            ejecutable = "dist/HerramientasBonos.exe"
        else:
            ejecutable = "dist/HerramientasBonos"
            
        if Path(ejecutable).exists():
            print(f"✅ ¡Ejecutable creado exitosamente!")
            print(f"📁 Ubicación: {os.path.abspath(ejecutable)}")
            
            # Mostrar tamaño del archivo
            size_mb = Path(ejecutable).stat().st_size / (1024 * 1024)
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

def limpiar_archivos_temp():
    """Limpia archivos temporales de PyInstaller"""
    carpetas_temp = ["build", "__pycache__"]
    archivos_temp = ["*.spec"]
    
    print("🧹 Limpiando archivos temporales...")
    
    for carpeta in carpetas_temp:
        if Path(carpeta).exists():
            try:
                import shutil
                shutil.rmtree(carpeta)
                print(f"   ✅ Eliminada carpeta: {carpeta}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {carpeta}: {e}")
    
    # Limpiar archivos .spec
    for spec_file in Path(".").glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"   ✅ Eliminado archivo: {spec_file}")
        except Exception as e:
            print(f"   ⚠️  No se pudo eliminar {spec_file}: {e}")

def test_dependencies():
    """Verifica que todas las dependencias estén disponibles"""
    print("🔍 Verificando dependencias...")
    
    required_packages = ["requests", "pandas"]
    optional_packages = ["openpyxl", "xlsxwriter"]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"   ❌ {package} (requerido)")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing_optional.append(package)
            print(f"   ⚠️  {package} (opcional)")
    
    if missing_required:
        print(f"\n❌ Faltan dependencias requeridas: {', '.join(missing_required)}")
        print("   Instálalas con:")
        print(f"   pip install {' '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  Dependencias opcionales faltantes: {', '.join(missing_optional)}")
        print("   Para funcionalidad completa, instálalas con:")
        print(f"   pip install {' '.join(missing_optional)}")
    
    return True

def create_spec_file():
    """Crea un archivo .spec personalizado para mayor control"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Detectar framework Qt
qt_framework = None
try:
    import PyQt6
    qt_framework = "PyQt6"
except ImportError:
    try:
        import PySide6
        qt_framework = "PySide6"
    except ImportError:
        raise ImportError("No se encontró PyQt6 ni PySide6")

print(f"Usando {{qt_framework}}")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('principal.py', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        qt_framework,
        f'{{qt_framework}}.QtCore',
        f'{{qt_framework}}.QtGui',
        f'{{qt_framework}}.QtWidgets',
        'requests',
        'pandas',
        'json',
        'csv',
        'tempfile',
        'datetime',
        'pathlib',
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
        'PyQt5',
        'PySide2',
        'nicegui',
        'fastapi',
        'uvicorn',
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

# Para macOS, crear también el bundle .app
import sys
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='HerramientasBonos.app',
        icon=None,
        bundle_identifier='com.rinorisk.herramientasbonos',
        version='2.0.0',
        info_plist={{
            'CFBundleName': 'Herramientas Bonos',
            'CFBundleDisplayName': 'Herramientas Bonos',
            'CFBundleVersion': '2.0.0',
            'CFBundleShortVersionString': '2.0.0',
            'NSHighResolutionCapable': True,
        }},
    )
'''
    
    with open("herramientas_bonos.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Archivo .spec creado")

if __name__ == "__main__":
    print("🚀 Iniciando proceso de construcción del ejecutable")
    print("=" * 60)
    
    # Verificar dependencias
    if not test_dependencies():
        print("\n❌ Verifica las dependencias antes de continuar")
        sys.exit(1)
    
    # Instalar PyInstaller si es necesario
    if not install_pyinstaller():
        sys.exit(1)
    
    # Crear archivo .spec personalizado
    create_spec_file()
    
    # Construir el ejecutable
    if build_executable():
        print("\n🎉 ¡Proceso completado exitosamente!")
        
        # Preguntar si limpiar archivos temporales
        try:
            respuesta = input("\n¿Deseas limpiar archivos temporales? (s/n): ")
            if respuesta.lower() in ['s', 'sí', 'si', 'y', 'yes']:
                limpiar_archivos_temp()
        except KeyboardInterrupt:
            print("\n\n👋 Proceso cancelado por el usuario")
        
        print("\n📋 Instrucciones de distribución:")
        print("   • El ejecutable está listo para distribuir")
        print("   • No requiere instalación de Python en el sistema destino")
        print("   • Incluye todas las dependencias necesarias")
        
    else:
        print("\n❌ El proceso falló. Revisa los errores anteriores.")
        sys.exit(1) 