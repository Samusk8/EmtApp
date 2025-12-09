#!/usr/bin/env python3
"""
Script de debug para probar la API de líneas, direcciones y paradas EMT
"""

import requests

TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI3ODQ1ODUiLCJpYXQiOjE3NjE1NjkzNzcsImV4cCI6MzMzOTQ0OTM3NywidXNlcm5hbWUiOiIxNzYxNTY5Mzc3NTE0M0ZLMUlJSVo0MEo2V0tCNklSNlUiLCJ0b2tlbl9kZXZpY2UiOiJmNTJiMjdiZjQyMjNjNTdhYWUxNDg4ZjU3OGE2OTdjNDk3OWIzNTNlZjZjODEyZmQwMTM3NGNlNGY2ODE5OWE1IiwiZGV2aWNlX3R5cGVfaWQiOjMsInJvbGVzIjoiQU5PTklNTyJ9.CxsRngyK_nO4sJ0CIk8KTvT5wajMlddceH2dgNVJCyZjSj6LnahPar4deHSfr1In"

HEADERS = {
    "Authorization": TOKEN,
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def test_lines_api():
    print("🔍 Probando API de líneas...")
    url = "https://www.emtpalma.cat/maas/api/v1/agency/lines/"
    print(f"URL: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Líneas encontradas: {len(data)}")
        for i, line in enumerate(data[:30]):
            print(f"  Línea {i+1}: {line.get('code')} - {line.get('name')}")
        return data
    else:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return None

def test_directions_api(line_id):
    print(f"\n🔍 Probando direcciones para línea ID {line_id}...")
    url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_id}/sublines"
    print(f"URL: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Direcciones encontradas: {len(data)}")
        for i, d in enumerate(data):
            print(f"  Dirección {i+1}: ID={d.get('id')}, Nombre={d.get('name')}")
        return data
    else:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return None

def test_stops_api(line_id, direction_id):
    print(f"\n🔍 Probando paradas para línea ID {line_id}, dirección ID {direction_id}...")
    url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_id}/stops?tripId={direction_id}&isLine=0&isLineNearStop=0&both=1"
    print(f"URL: {url}")

    resp = requests.get(url, headers=HEADERS, timeout=15)
    print(f"Status Code: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Paradas encontradas: {len(data)}")
        for i, stop in enumerate(data[:30]):
            print(f"  Parada {i+1}: {stop.get('code')} - {stop.get('name')} ({stop.get('latitude')}, {stop.get('longitude')})")
        return data
    else:
        print(f"❌ Error: {resp.status_code}")
        print(resp.text)
        return None

def main():
    lines = test_lines_api()
    if not lines:
        print("❌ No se pudieron cargar líneas")
        return

    for line in lines[:30]:
        line_id = line.get("id")
        directions = test_directions_api(line_id)
        if directions:
            first_dir = directions[0]
            direction_id = first_dir.get("id")
            if direction_id:
                test_stops_api(line_id, direction_id)

if __name__ == "__main__":
    main()
