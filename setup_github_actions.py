#!/usr/bin/env python3
"""
Script para configurar GitHub Actions para compilación automática
Permite generar ejecutables de Windows sin necesidad de Wine o máquina virtual
"""

import subprocess
import sys
import platform
import os
from pathlib import Path
import json

def check_git():
    """Verifica si Git está configurado"""
    try:
        result = subprocess.run(["git", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git detectado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git no está funcionando correctamente")
            return False
    except FileNotFoundError:
        print("❌ Git no está instalado")
        print("   Instálalo desde: https://git-scm.com/")
        return False

def check_github_repo():
    """Verifica si estamos en un repositorio de GitHub"""
    try:
        result = subprocess.run(["git", "remote", "-v"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and "github.com" in result.stdout:
            print("✅ Repositorio de GitHub detectado")
            return True
        else:
            print("❌ No se detectó un repositorio de GitHub")
            return False
    except subprocess.CalledProcessError:
        print("❌ Error al verificar el repositorio")
        return False

def create_workflow_directory():
    """Crea el directorio para GitHub Actions"""
    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directorio creado: {workflow_dir}")
    return workflow_dir

def create_workflow_file():
    """Crea el archivo de workflow para GitHub Actions"""
    workflow_content = '''name: Build Windows Executable

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:  # Permite ejecución manual

jobs:
  build-windows:
    runs-on: windows-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install PySide6 pyinstaller requests pandas openpyxl xlsxwriter
        
    - name: Build executable
      run: |
        python build_windows.py
        
    - name: Upload executable
      uses: actions/upload-artifact@v4
      with:
        name: HerramientasBonos-Windows
        path: dist/HerramientasBonos.exe
        
    - name: Create release
      if: github.event_name == 'push' && github.ref == 'refs/heads/main'
      uses: softprops/action-gh-release@v1
      with:
        files: dist/HerramientasBonos.exe
        tag_name: v${{ github.run_number }}
        name: Release v${{ github.run_number }}
        body: |
          ## Herramientas Bonos - Windows Executable
          
          ### Cambios en esta versión:
          - Compilado automáticamente desde GitHub Actions
          - Compatible con Windows 10/11
          - Incluye todas las dependencias
          
          ### Instrucciones:
          1. Descarga el archivo `HerramientasBonos.exe`
          2. Ejecuta haciendo doble clic
          3. No requiere instalación de Python
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
'''
    
    workflow_file = Path(".github/workflows/build-windows.yml")
    with open(workflow_file, "w", encoding="utf-8") as f:
        f.write(workflow_content)
    
    print(f"✅ Workflow creado: {workflow_file}")
    return workflow_file

def commit_and_push():
    """Hace commit y push de los cambios"""
    try:
        # Agregar archivos
        subprocess.run(["git", "add", ".github/"], check=True)
        subprocess.run(["git", "add", "build_windows.py"], check=True)
        
        # Commit
        subprocess.run([
            "git", "commit", "-m", 
            "Add GitHub Actions workflow for Windows build"
        ], check=True)
        
        # Push
        subprocess.run(["git", "push"], check=True)
        
        print("✅ Cambios subidos a GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al subir cambios: {e}")
        return False

def show_instructions():
    """Muestra instrucciones de uso"""
    print("\n📋 INSTRUCCIONES PARA GITHUB ACTIONS:")
    print("=" * 50)
    print("1. El workflow se ejecutará automáticamente en:")
    print("   • Cada push a main/master")
    print("   • Cada pull request")
    print("   • Manualmente desde GitHub")
    print()
    print("2. Para ejecutar manualmente:")
    print("   • Ve a tu repositorio en GitHub")
    print("   • Pestaña 'Actions'")
    print("   • Selecciona 'Build Windows Executable'")
    print("   • Click en 'Run workflow'")
    print()
    print("3. Descargar el ejecutable:")
    print("   • Ve a la pestaña 'Actions'")
    print("   • Selecciona el workflow completado")
    print("   • Descarga 'HerramientasBonos-Windows'")
    print()
    print("4. Releases automáticos:")
    print("   • Se crean automáticamente en cada push a main")
    print("   • Ve a la pestaña 'Releases'")
    print("   • Descarga la última versión")
    print()
    print("💡 Ventajas de GitHub Actions:")
    print("   • No necesitas Wine o máquina virtual")
    print("   • Compilación automática en Windows real")
    print("   • Releases automáticos")
    print("   • Historial de versiones")

def main():
    print("🚀 CONFIGURADOR DE GITHUB ACTIONS")
    print("=" * 50)
    print("Este script configura GitHub Actions para compilar")
    print("automáticamente el ejecutable de Windows.")
    print()
    
    # Verificar Git
    if not check_git():
        sys.exit(1)
    
    # Verificar repositorio GitHub
    if not check_github_repo():
        print("\n📋 Para usar GitHub Actions:")
        print("1. Crea un repositorio en GitHub")
        print("2. Sube tu código:")
        print("   git remote add origin https://github.com/usuario/repositorio.git")
        print("   git push -u origin main")
        print("3. Ejecuta este script nuevamente")
        sys.exit(1)
    
    # Crear directorio y archivo
    create_workflow_directory()
    create_workflow_file()
    
    # Preguntar si hacer commit y push
    try:
        respuesta = input("\n¿Deseas subir estos cambios a GitHub? (s/n): ")
        if respuesta.lower() in ['s', 'sí', 'si', 'y', 'yes']:
            if commit_and_push():
                print("\n🎉 ¡Configuración completada!")
                show_instructions()
            else:
                print("\n⚠️ Los archivos se crearon pero no se subieron")
                print("   Puedes subirlos manualmente con:")
                print("   git add .github/ build_windows.py")
                print("   git commit -m 'Add GitHub Actions workflow'")
                print("   git push")
        else:
            print("\n📁 Los archivos se crearon localmente")
            print("   Puedes subirlos manualmente cuando quieras")
            show_instructions()
            
    except KeyboardInterrupt:
        print("\n\n👋 Proceso cancelado")
        print("Los archivos se crearon localmente")

if __name__ == "__main__":
    main() 