#!/usr/bin/env python3
"""
Versión de prueba simplificada para verificar la corrección
"""

import sys
import requests
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QScrollArea
from PyQt6.QtCore import Qt

TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI3ODQ1ODUiLCJpYXQiOjE3NjE1NjkzNzcsImV4cCI6MzMzOTQ0OTM3NywidXNlcm5hbWUiOiIxNzYxNTY5Mzc3NTE0M0ZLMUlJSVo0MEo2V0tCNklSNlUiLCJ0b2tlbl9kZXZpY2UiOiJmNTJiMjdiZjQyMjNjNTdhYWUxNDg4ZjU3OGE2OTdjNDk3OWIzNTNlZjZjODEyZmQwMTM3NGNlNGY2ODE5OWE1IiwiZGV2aWNlX3R5cGVfaWQiOjMsInJvbGVzIjoiQU5PTklNTyJ9.CxsRngyK_nO4sJ0CIk8KTvT5wajMlddceH2dgNVJCyZjSj6LnahPar4deHSfr1In"

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test EMT - Corrección de API")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("🧪 Test de Corrección - API EMT Direcciones")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Área de scroll para líneas
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.lines_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Área de resultados
        self.result_label = QLabel("Cargando líneas...")
        self.result_label.setStyleSheet("padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.result_label)
        
        # Cargar líneas
        self.load_lines()
    
    def load_lines(self):
        """Cargar líneas EMT"""
        try:
            headers = {
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
            
            resp = requests.get("https://www.emtpalma.cat/maas/api/v1/agency/lines/directions-subline?subLineId=881", headers=headers, timeout=10)
            
            if resp.status_code == 200:
                lines_data = resp.json()
                self.result_label.setText(f"✅ {len(lines_data)} líneas cargadas correctamente")
                
                # Mostrar primeras 5 líneas como botones
                for i, line in enumerate(lines_data[:5]):
                    line_code = line.get("code", "?")
                    line_name = line.get("name", "Sin nombre")
                    line_id = line.get("id", "?")
                    
                    button = QPushButton(f"🚌 {line_code} - {line_name} (ID: {line_id})")
                    button.setStyleSheet("""
                        QPushButton {
                            padding: 8px;
                            text-align: left;
                            background-color: #007cba;
                            color: white;
                            border: none;
                            border-radius: 4px;
                            margin: 2px;
                        }
                        QPushButton:hover {
                            background-color: #005a87;
                        }
                    """)
                    
                    button.clicked.connect(lambda checked, line_data=line: self.test_directions(line_data))
                    self.lines_layout.addWidget(button)
                    
            else:
                self.result_label.setText(f"❌ Error cargando líneas: {resp.status_code}")
                
        except Exception as e:
            self.result_label.setText(f"❌ Excepción: {e}")
    
    def test_directions(self, line_data):
        """Probar carga de direcciones"""
        line_code = line_data.get("code", "?")
        line_id = line_data.get("id", "?")
        line_name = line_data.get("name", "Sin nombre")
        
        self.result_label.setText(f"🔄 Probando direcciones para {line_code} (ID: {line_id})...")
        
        try:
            headers = {
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
            
            # Usar ID en lugar de código
            url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_id}/directions"
            print(f"Probando URL: {url}")
            
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                directions = resp.json()
                
                if directions and len(directions) > 0:
                    result_text = f"✅ Línea {line_code}: {len(directions)} direcciones encontradas\n\n"
                    for i, direction in enumerate(directions):
                        dir_name = direction.get("name", "Sin nombre")
                        dir_id = direction.get("id", "?")
                        result_text += f"  {i+1}. {dir_name} (ID: {dir_id})\n"
                else:
                    result_text = f"ℹ️ Línea {line_code}: API funciona correctamente pero no hay direcciones configuradas"
                
                self.result_label.setText(result_text)
                
            else:
                self.result_label.setText(f"❌ Error HTTP {resp.status_code} para línea {line_code}")
                
        except Exception as e:
            self.result_label.setText(f"❌ Excepción probando {line_code}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())