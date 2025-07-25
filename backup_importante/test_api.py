#!/usr/bin/env python3
"""
Script de prueba para las APIs de login y comparación
Prueba independiente para verificar que las APIs funcionan correctamente
"""

import requests
import json
from datetime import datetime

def test_login():
    """Prueba la API de login"""
    print("🔐 [TEST] Probando API de Login...")
    
    url = "https://condicionesrino.com/api/core/auth/login"
    data = {
        "correo": "desarrollo-general@rinorisk.com",
        "password": "$QV@Rj4m66b"
    }
    headers = {"Content-Type": "application/json"}
    
    print(f"📡 [TEST] POST {url}")
    print(f"📊 [TEST] Datos: {data}")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"📈 [TEST] Status Code: {response.status_code}")
        print(f"📄 [TEST] Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            
            if token:
                print(f"✅ [TEST] Login EXITOSO")
                print(f"🎫 [TEST] Token obtenido: {token[:50]}...{token[-20:]}")
                return token
            else:
                print(f"❌ [TEST] Login exitoso pero sin token")
                print(f"📋 [TEST] Respuesta: {json.dumps(result, indent=2)}")
                return None
        else:
            print(f"❌ [TEST] Login FALLÓ")
            print(f"📄 [TEST] Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"💥 [TEST] Error en login: {e}")
        return None

def test_comparacion(token, periodo="2025-04-01"):
    """Prueba la API de comparación"""
    print(f"\n📊 [TEST] Probando API de Comparación...")
    
    url = f"https://condicionesrino.com/api/comparacion-adm?periodo[]={periodo}"
    
    # Probar diferentes formatos de headers
    headers_to_test = [
        {"Authorization": f"Bearer {token}"},
        {"authorization": f"Bearer {token}"},
        {"Authorization": f"bearer {token}"},
        {"Authorization": token},
        {"x-access-token": token},
        {"token": token},
        {"X-Auth-Token": token},
        {"Authorization": f"JWT {token}"},
        {"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    ]
    
    for i, headers in enumerate(headers_to_test, 1):
        print(f"\n🔄 [TEST] Prueba Header {i}/{len(headers_to_test)}")
        print(f"📡 [TEST] GET {url}")
        print(f"🔑 [TEST] Headers: {headers}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"📈 [TEST] Status Code: {response.status_code}")
            print(f"📡 [TEST] URL Real enviada: {response.url}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ [TEST] Comparación EXITOSA con headers formato {i}")
                print(f"📋 [TEST] Keys en respuesta: {list(result.keys())}")
                
                data = result.get('data', [])
                print(f"📊 [TEST] Registros en 'data': {len(data)}")
                
                if data and len(data) > 0:
                    primer_registro = data[0]
                    print(f"🔍 [TEST] Keys del primer registro: {list(primer_registro.keys())}")
                    
                    if 'resumenComparacion' in primer_registro:
                        resumen = primer_registro['resumenComparacion']
                        print(f"📈 [TEST] Resumen encontrado:")
                        print(f"  - Agentes: {resumen.get('agentes', 'N/A')}")
                        print(f"  - Pólizas: {resumen.get('cantidadPolizas', 'N/A')}")
                        print(f"  - Prima ADM: {resumen.get('totalPrimaADM', 'N/A')}")
                
                print(f"🎯 [TEST] FORMATO EXITOSO: {headers}")
                return headers  # Retornar los headers que funcionaron
                
            elif response.status_code == 401:
                print(f"❌ [TEST] Error 401: {response.text}")
                
            else:
                print(f"❌ [TEST] Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"💥 [TEST] Error en comparación: {e}")
    
    return None

def main():
    """Función principal de pruebas"""
    print("🚀 [TEST] Iniciando pruebas de API...")
    print("=" * 60)
    
    # Paso 1: Probar login
    token = test_login()
    
    if not token:
        print("\n❌ [TEST] No se pudo obtener token. Abortando pruebas.")
        return
    
    # Paso 2: Probar comparación
    working_headers = test_comparacion(token)
    
    print("\n" + "=" * 60)
    if working_headers:
        print("🎉 [TEST] ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("✅ [TEST] Las APIs funcionan correctamente")
        print(f"🎯 [TEST] Headers que funcionan: {working_headers}")
        return working_headers
    else:
        print("❌ [TEST] FALLÓ la prueba de comparación")
        print("🔍 [TEST] Ningún formato de header funcionó")
        return None

if __name__ == "__main__":
    main() 