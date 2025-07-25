#!/usr/bin/env python3
"""
Script para probar API con sesión persistente y cookies
"""

import requests
import json

def test_with_session():
    """Prueba usando requests.Session para mantener cookies"""
    print("🍪 [TEST] Probando con Session y Cookies...")
    
    # Crear sesión que mantendrá cookies
    session = requests.Session()
    
    # Paso 1: Login
    print("🔐 [TEST] Login con sesión...")
    login_url = "https://condicionesrino.com/api/core/auth/login"
    login_data = {
        "correo": "desarrollo-general@rinorisk.com",
        "password": "$QV@Rj4m66b"
    }
    
    try:
        login_response = session.post(login_url, json=login_data, timeout=10)
        print(f"📈 [TEST] Login Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ [TEST] Login falló: {login_response.text}")
            return
        
        result = login_response.json()
        token = result.get('token')
        
        if not token:
            print("❌ [TEST] No se obtuvo token")
            return
            
        print(f"✅ [TEST] Token obtenido: {token[:50]}...")
        print(f"🍪 [TEST] Cookies después del login: {dict(session.cookies)}")
        
        # Paso 2: Probar comparación con la misma sesión (sin headers)
        print("\n📊 [TEST] Probando comparación con sesión (sin token en headers)...")
        comp_url = "https://condicionesrino.com/api/comparacion-adm?periodo[]=2025-04-01"
        
        comp_response = session.get(comp_url, timeout=10)
        print(f"📈 [TEST] Comparación Status: {comp_response.status_code}")
        
        if comp_response.status_code == 200:
            print("🎉 [TEST] ¡FUNCIONA CON SESIÓN!")
            data = comp_response.json()
            print(f"📊 [TEST] Keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ [TEST] Error: {comp_response.text}")
        
        # Paso 3: Probar con sesión Y token en header
        print("\n📊 [TEST] Probando comparación con sesión + token en header...")
        headers = {"Authorization": f"Bearer {token}"}
        
        comp_response2 = session.get(comp_url, headers=headers, timeout=10)
        print(f"📈 [TEST] Status: {comp_response2.status_code}")
        
        if comp_response2.status_code == 200:
            print("🎉 [TEST] ¡FUNCIONA CON SESIÓN + TOKEN!")
            data = comp_response2.json()
            print(f"📊 [TEST] Keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ [TEST] Error: {comp_response2.text}")
            
    except Exception as e:
        print(f"💥 [TEST] Error: {e}")
    
    return False

def test_endpoint_variations():
    """Prueba diferentes variaciones del endpoint"""
    print("\n🔍 [TEST] Probando variaciones del endpoint...")
    
    # Hacer login simple para obtener token
    login_url = "https://condicionesrino.com/api/core/auth/login"
    login_data = {
        "correo": "desarrollo-general@rinorisk.com",
        "password": "$QV@Rj4m66b"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        token = response.json().get('token')
        
        if not token:
            print("❌ [TEST] No se pudo obtener token")
            return
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Diferentes variaciones del endpoint
        endpoints = [
            "https://condicionesrino.com/api/comparacion-adm?periodo[]=2025-04-01",
            "https://condicionesrino.com/api/comparacion-adm?periodo=2025-04-01",
            "https://condicionesrino.com/api/comparacion-adm/2025-04-01",
            "https://condicionesrino.com/api/comparacion?periodo[]=2025-04-01",
            "https://condicionesrino.com/api/admin/comparacion?periodo[]=2025-04-01",
            "https://condicionesrino.com/comparacion-adm?periodo[]=2025-04-01",
        ]
        
        for i, endpoint in enumerate(endpoints, 1):
            print(f"\n🔄 [TEST] Endpoint {i}/{len(endpoints)}")
            print(f"📡 [TEST] {endpoint}")
            
            try:
                resp = requests.get(endpoint, headers=headers, timeout=5)
                print(f"📈 [TEST] Status: {resp.status_code}")
                
                if resp.status_code == 200:
                    print(f"🎉 [TEST] ¡ENDPOINT FUNCIONAL ENCONTRADO!")
                    data = resp.json()
                    print(f"📊 [TEST] Keys: {list(data.keys())}")
                    return endpoint
                elif resp.status_code == 404:
                    print("❌ [TEST] Endpoint no existe")
                elif resp.status_code == 401:
                    print(f"❌ [TEST] Error 401: {resp.text}")
                else:
                    print(f"❌ [TEST] Error {resp.status_code}: {resp.text}")
                    
            except Exception as e:
                print(f"💥 [TEST] Error: {e}")
        
    except Exception as e:
        print(f"💥 [TEST] Error en login: {e}")
    
    return None

def main():
    """Función principal"""
    print("🚀 [TEST] Script de prueba con sesiones y endpoints...")
    print("=" * 60)
    
    # Prueba 1: Con sesión persistente
    session_works = test_with_session()
    
    if session_works:
        print("\n✅ [TEST] ¡LA SESIÓN FUNCIONA!")
        return
    
    # Prueba 2: Diferentes endpoints
    working_endpoint = test_endpoint_variations()
    
    print("\n" + "=" * 60)
    if working_endpoint:
        print(f"🎉 [TEST] ¡ENDPOINT FUNCIONAL: {working_endpoint}")
    else:
        print("❌ [TEST] NINGÚN MÉTODO FUNCIONÓ")
        print("🤔 [TEST] Posibles problemas:")
        print("   - API temporalmente inaccesible")
        print("   - Cambios en la configuración del servidor")
        print("   - Middleware de autenticación malconfigurado")

if __name__ == "__main__":
    main() 