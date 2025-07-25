#!/usr/bin/env python3
"""
Script para crear un instalador .dmg para Admin Bonos en macOS
Requiere: PyInstaller, create-dmg (homebrew)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuración
APP_NAME = "Admin Bonos"
APP_VERSION = "1.0.0"
BUNDLE_ID = "com.rinorisk.adminbonos"
MAIN_SCRIPT = "main.py"
ICON_PATH = "assets/img/logo.png"
DMG_NAME = f"AdminBonos-{APP_VERSION}-macOS"

def run_command(cmd, description):
    """Ejecuta un comando y maneja errores"""
    print(f"\n🔧 {description}")
    print(f"💻 Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"📤 Stdout: {e.stdout}")
        if e.stderr:
            print(f"📥 Stderr: {e.stderr}")
        return False

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias...")
    
    # Verificar PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller disponible")
    except ImportError:
        print("❌ PyInstaller no está instalado. Instálalo con: pip install pyinstaller")
        return False
    
    # Verificar create-dmg (opcional)
    try:
        result = subprocess.run(["create-dmg", "--version"], capture_output=True)
        if result.returncode == 0:
            print("✅ create-dmg disponible")
        else:
            print("⚠️ create-dmg no está disponible, se usará método alternativo")
    except FileNotFoundError:
        print("⚠️ create-dmg no está instalado. Opcional: brew install create-dmg")
    
    return True

def convert_icon():
    """Convierte PNG a ICNS para macOS"""
    print("🎨 Convirtiendo icono...")
    
    if not os.path.exists(ICON_PATH):
        print(f"❌ No se encontró el icono en {ICON_PATH}")
        return None
    
    # Crear iconset
    iconset_path = "assets/img/logo.iconset"
    icns_path = "assets/img/logo.icns"
    
    # Crear directorio iconset
    os.makedirs(iconset_path, exist_ok=True)
    
    # Generar diferentes tamaños usando sips (nativo de macOS)
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        # Crear versiones normales
        cmd = [
            "sips", "-z", str(size), str(size), 
            ICON_PATH, "--out", f"{iconset_path}/icon_{size}x{size}.png"
        ]
        if not run_command(cmd, f"Generando icono {size}x{size}"):
            print(f"⚠️ No se pudo generar icono {size}x{size}")
        
        # Crear versiones @2x para retina
        if size <= 512:
            cmd = [
                "sips", "-z", str(size*2), str(size*2), 
                ICON_PATH, "--out", f"{iconset_path}/icon_{size}x{size}@2x.png"
            ]
            run_command(cmd, f"Generando icono {size}x{size}@2x")
    
    # Convertir iconset a icns
    cmd = ["iconutil", "-c", "icns", iconset_path, "-o", icns_path]
    if run_command(cmd, "Convirtiendo a ICNS"):
        # Limpiar iconset temporal
        shutil.rmtree(iconset_path, ignore_errors=True)
        return icns_path
    
    return None

def build_app():
    """Construye la aplicación con PyInstaller"""
    print("🏗️ Construyendo aplicación...")
    
    # Convertir icono
    icon_path = convert_icon()
    
    # Preparar comando PyInstaller
    cmd = [
        "pyinstaller",
        "--onedir",  # Un directorio (mejor para macOS)
        "--windowed",  # Sin consola
        "--noconfirm",  # Sobrescribir sin preguntar
        "--clean",  # Limpiar caché
        f"--name={APP_NAME}",
        "--osx-bundle-identifier", BUNDLE_ID,
    ]
    
    # Agregar icono si está disponible
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # Agregar archivos adicionales
    cmd.extend([
        "--add-data", "assets:assets",
        "--add-data", "requirements.txt:.",
    ])
    
    # Archivo principal
    cmd.append(MAIN_SCRIPT)
    
    # Ejecutar PyInstaller
    if run_command(cmd, "Ejecutando PyInstaller"):
        print("✅ Aplicación construida exitosamente")
        return True
    else:
        print("❌ Error al construir la aplicación")
        return False

def create_dmg_simple():
    """Crea DMG usando método simple"""
    print("📦 Creando DMG (método simple)...")
    
    app_path = f"dist/{APP_NAME}.app"
    dmg_path = f"dist/{DMG_NAME}.dmg"
    
    if not os.path.exists(app_path):
        print(f"❌ No se encontró la aplicación en {app_path}")
        return False
    
    # Crear DMG temporal
    temp_dmg = f"dist/temp_{DMG_NAME}.dmg"
    
    # Estimar tamaño necesario (en MB)
    app_size = get_directory_size(app_path) // (1024 * 1024)
    dmg_size = max(app_size + 50, 100)  # Al menos 100MB
    
    # Crear DMG vacío
    cmd = [
        "hdiutil", "create", "-size", f"{dmg_size}m", 
        "-fs", "HFS+", "-volname", APP_NAME, temp_dmg
    ]
    
    if not run_command(cmd, "Creando DMG temporal"):
        return False
    
    # Montar DMG
    mount_result = subprocess.run(
        ["hdiutil", "mount", temp_dmg], 
        capture_output=True, text=True
    )
    
    if mount_result.returncode != 0:
        print("❌ Error al montar DMG")
        return False
    
    # Extraer punto de montaje
    mount_point = None
    for line in mount_result.stdout.split('\n'):
        if '/Volumes/' in line:
            mount_point = line.split('/Volumes/')[-1].strip()
            mount_point = f"/Volumes/{mount_point}"
            break
    
    if not mount_point:
        print("❌ No se pudo determinar el punto de montaje")
        return False
    
    print(f"📁 DMG montado en: {mount_point}")
    
    try:
        # Copiar aplicación
        dest_app = f"{mount_point}/{APP_NAME}.app"
        shutil.copytree(app_path, dest_app)
        print("✅ Aplicación copiada al DMG")
        
        # Crear enlace a Applications
        applications_link = f"{mount_point}/Applications"
        os.symlink("/Applications", applications_link)
        print("✅ Enlace a Applications creado")
        
    except Exception as e:
        print(f"❌ Error al copiar archivos: {e}")
        return False
    
    finally:
        # Desmontar DMG
        subprocess.run(["hdiutil", "unmount", mount_point], capture_output=True)
    
    # Convertir a DMG final comprimido
    cmd = [
        "hdiutil", "convert", temp_dmg, "-format", "UDZO", 
        "-o", dmg_path
    ]
    
    if run_command(cmd, "Comprimiendo DMG final"):
        # Limpiar DMG temporal
        os.remove(temp_dmg)
        print(f"✅ DMG creado: {dmg_path}")
        return True
    
    return False

def create_dmg_advanced():
    """Crea DMG usando create-dmg con diseño personalizado"""
    print("📦 Creando DMG (método avanzado)...")
    
    app_path = f"dist/{APP_NAME}.app"
    dmg_path = f"dist/{DMG_NAME}.dmg"
    
    if not os.path.exists(app_path):
        print(f"❌ No se encontró la aplicación en {app_path}")
        return False
    
    # Verificar si create-dmg está disponible
    try:
        subprocess.run(["create-dmg", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ create-dmg no disponible, usando método simple")
        return create_dmg_simple()
    
    # Crear DMG con create-dmg
    cmd = [
        "create-dmg",
        "--volname", APP_NAME,
        "--volicon", ICON_PATH if os.path.exists(ICON_PATH) else "assets/img/rino.png",
        "--window-pos", "200", "120",
        "--window-size", "600", "400",
        "--icon-size", "100",
        "--icon", f"{APP_NAME}.app", "175", "190",
        "--hide-extension", f"{APP_NAME}.app",
        "--app-drop-link", "425", "190",
        "--no-internet-enable",
        dmg_path,
        app_path
    ]
    
    if run_command(cmd, "Creando DMG con create-dmg"):
        print(f"✅ DMG creado: {dmg_path}")
        return True
    else:
        print("⚠️ Error con create-dmg, intentando método simple")
        return create_dmg_simple()

def get_directory_size(path):
    """Calcula el tamaño de un directorio en bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
    return total_size

def cleanup():
    """Limpia archivos temporales"""
    print("🧹 Limpiando archivos temporales...")
    
    # Limpiar build de PyInstaller
    if os.path.exists("build"):
        shutil.rmtree("build", ignore_errors=True)
        print("✅ Directorio build eliminado")
    
    # Limpiar spec file
    spec_file = f"{APP_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print("✅ Archivo .spec eliminado")
    
    # Limpiar iconos temporales
    icns_file = "assets/img/logo.icns"
    if os.path.exists(icns_file):
        os.remove(icns_file)
        print("✅ Archivo .icns temporal eliminado")

def main():
    """Función principal"""
    print("🚀 Iniciando construcción de instalador DMG para Admin Bonos")
    print(f"📱 Versión: {APP_VERSION}")
    print(f"🍎 Plataforma: macOS")
    
    # Verificar que estamos en macOS
    if sys.platform != "darwin":
        print("❌ Este script solo funciona en macOS")
        sys.exit(1)
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar archivo principal
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ No se encontró {MAIN_SCRIPT}")
        sys.exit(1)
    
    try:
        # Construir aplicación
        if not build_app():
            print("❌ Error al construir la aplicación")
            sys.exit(1)
        
        # Crear DMG
        dmg_created = create_dmg_advanced()
        
        if dmg_created:
            print("\n🎉 ¡Instalador DMG creado exitosamente!")
            print(f"📦 Archivo: dist/{DMG_NAME}.dmg")
            print(f"📁 Aplicación: dist/{APP_NAME}.app")
            
            # Mostrar información del archivo
            dmg_path = f"dist/{DMG_NAME}.dmg"
            if os.path.exists(dmg_path):
                size_mb = os.path.getsize(dmg_path) // (1024 * 1024)
                print(f"💾 Tamaño: {size_mb} MB")
        else:
            print("❌ Error al crear el DMG")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
    
    finally:
        # Limpiar archivos temporales
        cleanup()

if __name__ == "__main__":
    main() 