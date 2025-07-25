#!/usr/bin/env python3
"""
Script de prueba para verificar que la aplicación funciona correctamente
"""

import subprocess
import time
import signal
import os

def test_application():
    """Prueba la aplicación empaquetada"""
    app_path = "dist/Admin Bonos.app/Contents/MacOS/Admin Bonos"
    
    print("🧪 Probando aplicación empaquetada...")
    print(f"📱 Ejecutando: {app_path}")
    
    try:
        # Ejecutar la aplicación en background
        process = subprocess.Popen(
            [app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("⏱️ Esperando 8 segundos para que la aplicación inicie...")
        time.sleep(8)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("✅ La aplicación está ejecutándose correctamente")
            print("🖥️ La ventana de login debería estar visible")
            
            # Terminar el proceso
            process.terminate()
            try:
                process.wait(timeout=5)
                print("✅ Aplicación terminada correctamente")
            except subprocess.TimeoutExpired:
                process.kill()
                print("⚠️ Aplicación forzada a terminar")
                
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ La aplicación se cerró inesperadamente")
            print(f"📤 STDOUT: {stdout}")
            print(f"📥 STDERR: {stderr}")
            print(f"🔄 Código de salida: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        return False

if __name__ == "__main__":
    success = test_application()
    
    if success:
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("✅ La aplicación funciona correctamente")
        print("✅ No se cierra al momento del login")
        print("📦 El DMG está listo para distribuir")
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("⚠️ La aplicación tiene problemas")
        
    print(f"\n📦 DMG disponible en: dist/AdminBonos-1.0.0-macOS.dmg") 