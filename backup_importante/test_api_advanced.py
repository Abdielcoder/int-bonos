#!/usr/bin/env python3
"""
Script avanzado para probar diferentes métodos de envío del token
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

def test_token_methods(token, periodo="2025-04-01"):
    """Prueba diferentes métodos para enviar el token"""
    print(f"\n📊 [TEST] Probando diferentes métodos de token...")
    
    base_url = "https://condicionesrino.com/api/comparacion-adm"
    
    # Métodos a probar
    test_cases = [
        {
            "name": "Token en query parameter 'token'",
            "url": f"{base_url}?periodo[]={periodo}&token={token}",
            "headers": {},
            "method": "GET"
        },
        {
            "name": "Token en query parameter 'access_token'",
            "url": f"{base_url}?periodo[]={periodo}&access_token={token}",
            "headers": {},
            "method": "GET"
        },
        {
            "name": "POST con token en body",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "body": {"token": token}
        },
        {
            "name": "POST con authorization en body",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {"Content-Type": "application/json"},
            "method": "POST",
            "body": {"authorization": f"Bearer {token}"}
        },
        {
            "name": "Header Authorization sin Bearer",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {"Authorization": token},
            "method": "GET"
        },
        {
            "name": "Header con Token en mayúsculas",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {"TOKEN": token},
            "method": "GET"
        },
        {
            "name": "Header X-API-Key",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {"X-API-Key": token},
            "method": "GET"
        },
        {
            "name": "Múltiples headers posibles",
            "url": f"{base_url}?periodo[]={periodo}",
            "headers": {
                "Authorization": f"Bearer {token}",
                "x-access-token": token,
                "token": token,
                "X-API-Key": token
            },
            "method": "GET"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔄 [TEST] Prueba {i}/{len(test_cases)}: {test_case['name']}")
        print(f"📡 [TEST] {test_case['method']} {test_case['url'][:100]}...")
        print(f"🔑 [TEST] Headers: {test_case['headers']}")
        
        try:
            if test_case['method'] == 'GET':
                response = requests.get(
                    test_case['url'], 
                    headers=test_case['headers'], 
                    timeout=10
                )
            else:  # POST
                response = requests.post(
                    test_case['url'], 
                    headers=test_case['headers'],
                    json=test_case.get('body', {}),
                    timeout=10
                )
            
            print(f"📈 [TEST] Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"🎉 [TEST] ¡ÉXITO! Método que funciona: {test_case['name']}")
                result = response.json()
                print(f"📋 [TEST] Keys en respuesta: {list(result.keys())}")
                
                data = result.get('data', [])
                print(f"📊 [TEST] Registros: {len(data)}")
                
                if data and len(data) > 0:
                    primer_registro = data[0]
                    if 'resumenComparacion' in primer_registro:
                        resumen = primer_registro['resumenComparacion']
                        print(f"📈 [TEST] Agentes: {resumen.get('agentes', 'N/A')}")
                        print(f"📈 [TEST] Pólizas: {resumen.get('cantidadPolizas', 'N/A')}")
                
                return test_case
                
            elif response.status_code == 401:
                print(f"❌ [TEST] Error 401: {response.text}")
            elif response.status_code == 403:
                print(f"❌ [TEST] Error 403: {response.text}")
            elif response.status_code == 400:
                print(f"❌ [TEST] Error 400: {response.text}")
            else:
                print(f"❌ [TEST] Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"💥 [TEST] Error: {e}")
    
    return None

def main():
    """Función principal"""
    print("🚀 [TEST] Script avanzado de pruebas de API...")
    print("=" * 60)
    
    # Paso 1: Login
    token = test_login()
    if not token:
        print("❌ [TEST] No se pudo obtener token.")
        return
    
    # Paso 2: Probar diferentes métodos
    working_method = test_token_methods(token)
    
    print("\n" + "=" * 60)
    if working_method:
        print("🎉 [TEST] ¡MÉTODO EXITOSO ENCONTRADO!")
        print(f"✅ [TEST] {working_method['name']}")
        print(f"🔧 [TEST] Método: {working_method['method']}")
        print(f"🔧 [TEST] Headers: {working_method['headers']}")
        if 'body' in working_method:
            print(f"🔧 [TEST] Body: {working_method['body']}")
    else:
        print("❌ [TEST] NINGÚN MÉTODO FUNCIONÓ")
        print("🤔 [TEST] La API puede tener problemas o requiere un método no probado")

if __name__ == "__main__":
    main() 