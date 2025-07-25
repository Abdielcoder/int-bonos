#!/usr/bin/env python3
"""
Script definitivo usando el header x-token correcto
"""

import requests
import json

def test_login():
    """Prueba la API de login"""
    print("🔐 [TEST] Probando API de Login...")
    
    url = "https://condicionesrino.com/api/core/auth/login"
    data = {
        "correo": "desarrollo-general@rinorisk.com",
        "password": "$QV@Rj4m66b"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            token = result.get('token')
            if token:
                print(f"✅ [TEST] Login EXITOSO. Token: {token[:50]}...")
                return token
    except Exception as e:
        print(f"💥 [TEST] Error: {e}")
    
    return None

def test_comparacion_with_x_token(token, periodo="2025-04-01"):
    """Prueba la API de comparación usando x-token header"""
    print(f"\n📊 [TEST] Probando API de Comparación con x-token...")
    
    url = f"https://condicionesrino.com/api/comparacion-adm?periodo[]={periodo}"
    headers = {"x-token": token}  # ¡Este es el header correcto!
    
    print(f"📡 [TEST] GET {url}")
    print(f"🔑 [TEST] Headers: {headers}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📈 [TEST] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 [TEST] ¡ÉXITO CON X-TOKEN!")
            result = response.json()
            print(f"📋 [TEST] Keys en respuesta: {list(result.keys())}")
            
            data = result.get('data', [])
            print(f"📊 [TEST] Registros en 'data': {len(data)}")
            
            if data and len(data) > 0:
                primer_registro = data[0]
                print(f"🔍 [TEST] Keys del primer registro: {list(primer_registro.keys())}")
                
                if 'resumenComparacion' in primer_registro:
                    resumen = primer_registro['resumenComparacion']
                    print(f"📈 [TEST] Resumen encontrado:")
                    print(f"  - Período: {primer_registro.get('periodo', 'N/A')}")
                    print(f"  - Agentes: {resumen.get('agentes', 'N/A')}")
                    print(f"  - Pólizas: {resumen.get('cantidadPolizas', 'N/A')}")
                    print(f"  - Prima ADM: ${resumen.get('totalPrimaADM', 'N/A'):,}")
                    print(f"  - Prima Proyectada: ${resumen.get('totalPrimaProyectada', 'N/A'):,}")
                    print(f"  - Diferencia Pólizas: {resumen.get('cantidadPolizasDiferencia', 'N/A')}")
            
            return result
            
        else:
            print(f"❌ [TEST] Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 [TEST] Error: {e}")
    
    return None

def main():
    """Función principal"""
    print("🚀 [TEST] Script definitivo - Usando x-token header...")
    print("=" * 60)
    
    # Paso 1: Login
    token = test_login()
    if not token:
        print("❌ [TEST] No se pudo obtener token.")
        return None
    
    # Paso 2: Comparación con x-token
    datos = test_comparacion_with_x_token(token)
    
    print("\n" + "=" * 60)
    if datos:
        print("🎉 [TEST] ¡INTEGRACIÓN EXITOSA!")
        print("✅ [TEST] La API funciona correctamente usando x-token")
        print("🔧 [TEST] Header correcto: x-token")
        return {
            "token": token,
            "datos": datos,
            "header_method": "x-token"
        }
    else:
        print("❌ [TEST] Aún hay problemas con la API")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🎯 [SOLUCIÓN] Token: {result['token'][:50]}...")
        print(f"🎯 [SOLUCIÓN] Header: {result['header_method']}")
        print(f"🎯 [SOLUCIÓN] Datos obtenidos: {len(result['datos'].get('data', []))} registros") 