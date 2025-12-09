#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de EMT Palma
"""

import sys
import requests
from PyQt6.QtWidgets import QApplication, QMessageBox

# Token de la API EMT
TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI3ODQ1ODUiLCJpYXQiOjE3NjE1NjkzNzcsImV4cCI6MzMzOTQ0OTM3NywidXNlcm5hbWUiOiIxNzYxNTY5Mzc3NTE0M0ZLMUlJSVo0MEo2V0tCNklSNlUiLCJ0b2tlbl9kZXZpY2UiOiJmNTJiMjdiZjQyMjNjNTdhYWUxNDg4ZjU3OGE2OTdjNDk3OWIzNTNlZjZjODEyZmQwMTM3NGNlNGY2ODE5OWE1IiwiZGV2aWNlX3R5cGVfaWQiOjMsInJvbGVzIjoiQU5PTklNTyJ9.CxsRngyK_nO4sJ0CIk8KTvT5wajMlddceH2dgNVJCyZjSj6LnahPar4deHSfr1In"

def test_api_connection():
    """Probar conexión con la API EMT"""
    print("🔍 Probando conexión con API EMT Palma...")
    
    headers = {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        # Probar endpoint de líneas
        url = "https://www.emtpalma.cat/maas/api/v1/agency/lines/"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ API conectada correctamente")
            print(f"📊 Líneas disponibles: {len(data)}")
            
            # Mostrar algunas líneas de ejemplo
            for i, line in enumerate(data[:5]):
                code = line.get("code", "?")
                name = line.get("name", "Sin nombre")
                color = line.get("routeColor", "000000")
                print(f"   🚌 Línea {code}: {name} (#{color})")
            
            if len(data) > 5:
                print(f"   ... y {len(data) - 5} líneas más")
                
            return True
        else:
            print(f"❌ Error API: HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_specific_line():
    """Probar consulta de una línea específica"""
    print("\n🔍 Probando consulta de línea específica...")
    
    headers = {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        # Probar línea 1 (suele existir)
        line_code = "1"
        url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_code}/directions"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            directions = resp.json()
            print(f"✅ Línea {line_code} encontrada")
            print(f"📍 Direcciones disponibles: {len(directions)}")
            
            for direction in directions:
                dir_name = direction.get("name", "Sin nombre")
                dir_id = direction.get("id", "?")
                print(f"   🎯 {dir_id}: {dir_name}")
                
            return True
        else:
            print(f"❌ Error consultando línea {line_code}: HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_stop_query():
    """Probar consulta de parada"""
    print("\n🔍 Probando consulta de parada...")
    
    headers = {
        "Authorization": TOKEN,
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    
    try:
        # Probar parada 1 (Plaza España suele ser la 1)
        stop_code = "1"
        url = f"https://www.emtpalma.cat/maas/api/v1/agency/stops/{stop_code}/timestr"
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Parada {stop_code} encontrada")
            print(f"🚌 Líneas que pasan: {len(data)}")
            
            for entry in data[:3]:  # Mostrar solo las primeras 3
                line = entry.get("lineCode", "?")
                vehicles = entry.get("vehicles", [])
                print(f"   🚌 Línea {line}: {len(vehicles)} vehículos")
                
            return True
        else:
            print(f"❌ Error consultando parada {stop_code}: HTTP {resp.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_dependencies():
    """Verificar dependencias instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("PyQt6-WebEngine", "PyQt6.QtWebEngineWidgets"),
        ("Folium", "folium"),
        ("Requests", "requests")
    ]
    
    all_ok = True
    
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name} instalado correctamente")
        except ImportError:
            print(f"❌ {name} NO encontrado - ejecuta: pip install {name.lower()}")
            all_ok = False
    
    return all_ok

def main():
    """Función principal de pruebas"""
    print("=" * 50)
    print("🧪 PRUEBAS EMT PALMA APPLICATION")
    print("=" * 50)
    
    # Verificar dependencias
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Faltan dependencias. Instala con:")
        print("   pip install -r requirements.txt")
        return False
    
    # Probar API
    api_ok = test_api_connection()
    
    if not api_ok:
        print("\n❌ No se puede conectar con la API EMT")
        print("   Verifica tu conexión a internet")
        return False
    
    # Pruebas específicas
    line_ok = test_specific_line()
    stop_ok = test_stop_query()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 50)
    print(f"Dependencias: {'✅ OK' if deps_ok else '❌ FALLO'}")
    print(f"API EMT:      {'✅ OK' if api_ok else '❌ FALLO'}")
    print(f"Consulta línea: {'✅ OK' if line_ok else '❌ FALLO'}")
    print(f"Consulta parada: {'✅ OK' if stop_ok else '❌ FALLO'}")
    
    if all([deps_ok, api_ok, line_ok, stop_ok]):
        print("\n🎉 ¡Todas las pruebas pasaron! La aplicación debería funcionar correctamente.")
        print("   Ejecuta: python app_final.py")
        return True
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    
    # Si hay PyQt6 disponible, mostrar diálogo
    try:
        app = QApplication(sys.argv)
        if success:
            QMessageBox.information(
                None, 
                "Pruebas Completadas", 
                "✅ Todas las pruebas pasaron!\n\nLa aplicación está lista para usar.\nEjecuta: python app_final.py"
            )
        else:
            QMessageBox.warning(
                None,
                "Pruebas Fallidas", 
                "❌ Algunas pruebas fallaron.\n\nRevisa la consola para más detalles."
            )
    except ImportError:
        pass  # PyQt6 no disponible, solo mostrar en consola
    
    sys.exit(0 if success else 1)