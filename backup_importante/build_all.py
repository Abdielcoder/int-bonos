#!/usr/bin/env python3
"""
Script principal para crear ejecutables en macOS y Windows
Detecta automáticamente el sistema operativo y ejecuta el script correspondiente
"""

import subprocess
import sys
import platform
import os
from pathlib import Path

def detect_os():
    """Detecta el sistema operativo actual"""
    sistema = platform.system()
    print(f"🖥️  Sistema detectado: {sistema}")
    
    if sistema == "Darwin":
        return "macos"
    elif sistema == "Windows":
        return "windows"
    else:
        return "unsupported"

def build_for_macos():
    """Ejecuta el script de construcción para macOS"""
    print("🍎 Ejecutando construcción para macOS...")
    
    script_path = Path("build_macos.py")
    if not script_path.exists():
        print("❌ No se encontró build_macos.py")
        return False
    
    try:
        result = subprocess.run([sys.executable, "build_macos.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar build_macos.py: {e}")
        return False

def build_for_windows():
    """Ejecuta el script de construcción para Windows"""
    print("🪟 Ejecutando construcción para Windows...")
    
    script_path = Path("build_windows.py")
    if not script_path.exists():
        print("❌ No se encontró build_windows.py")
        return False
    
    try:
        result = subprocess.run([sys.executable, "build_windows.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar build_windows.py: {e}")
        return False

def build_for_windows_wine():
    """Ejecuta el script de construcción para Windows usando Wine"""
    print("🍷 Ejecutando construcción para Windows con Wine...")
    
    script_path = Path("build_windows_wine.py")
    if not script_path.exists():
        print("❌ No se encontró build_windows_wine.py")
        return False
    
    try:
        result = subprocess.run([sys.executable, "build_windows_wine.py"], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar build_windows_wine.py: {e}")
        return False

def show_instructions():
    """Muestra instrucciones de uso"""
    print("\n📋 INSTRUCCIONES DE USO:")
    print("=" * 50)
    print("1. Para macOS:")
    print("   • Ejecuta: python3 build_macos.py")
    print("   • O ejecuta: python3 build_all.py")
    print("   • Resultado: dist/HerramientasBonos.app")
    print()
    print("2. Para Windows:")
    print("   • Ejecuta: python build_windows.py")
    print("   • O ejecuta: python build_all.py")
    print("   • Resultado: dist/HerramientasBonos.exe")
    print()
    print("3. Para Windows desde macOS (usando Wine):")
    print("   • Ejecuta: python3 build_windows_wine.py")
    print("   • Requiere Wine instalado")
    print("   • Resultado: dist/HerramientasBonos.exe")
    print()
    print("4. Características:")
    print("   • Usa solo PySide6 (sin conflictos con PyQt6)")
    print("   • Incluye todas las dependencias necesarias")
    print("   • No requiere Python en el sistema destino")
    print("   • Interfaz gráfica sin consola")
    print()
    print("5. Distribución:")
    print("   • macOS: Comprime la carpeta .app")
    print("   • Windows: Comparte el archivo .exe")
    print("   • Ambos son ejecutables independientes")

def main():
    print("🚀 CONSTRUCTOR DE EJECUTABLES - HERRAMIENTAS BONOS")
    print("=" * 60)
    
    # Detectar sistema operativo
    os_type = detect_os()
    
    if os_type == "macos":
        print("🍎 Construyendo para macOS...")
        success = build_for_macos()
    elif os_type == "windows":
        print("🪟 Construyendo para Windows...")
        success = build_for_windows()
    else:
        print(f"❌ Sistema operativo no soportado: {platform.system()}")
        print("   Solo se soporta macOS y Windows")
        sys.exit(1)
    
    if success:
        print("\n🎉 ¡Construcción completada exitosamente!")
        
        # Mostrar ubicación del ejecutable
        if os_type == "macos":
            app_path = Path("dist/HerramientasBonos.app")
            if app_path.exists():
                print(f"📁 Ejecutable: {app_path.absolute()}")
        else:
            exe_path = Path("dist/HerramientasBonos.exe")
            if exe_path.exists():
                print(f"📁 Ejecutable: {exe_path.absolute()}")
        
        print("\n✅ El ejecutable está listo para usar y distribuir")
    else:
        print("\n❌ La construcción falló")
        print("   Revisa los errores anteriores")
        sys.exit(1)

if __name__ == "__main__":
    # Si se ejecuta directamente, mostrar instrucciones
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        show_instructions()
    else:
        main() 