import sys
import os
import math
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                            QPushButton, QScrollArea, QWidget, QMessageBox)
from PyQt6.QtCore import QObject, pyqtSignal, Qt, QThread, pyqtSlot
from PyQt6 import QtCore
from View.mainWindowUi2 import Ui_MainWindow
from map_package_enhanced import MapWindow

TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI3ODQ1ODUiLCJpYXQiOjE3NjE1NjkzNzcsImV4cCI6MzMzOTQ0OTM3NywidXNlcm5hbWUiOiIxNzYxNTY5Mzc3NTE0M0ZLMUlJSVo0MEo2V0tCNklSNlUiLCJ0b2tlbl9kZXZpY2UiOiJmNTJiMjdiZjQyMjNjNTdhYWUxNDg4ZjU3OGE2OTdjNDk3OWIzNTNlZjZjODEyZmQwMTM3NGNlNGY2ODE5OWE1IiwiZGV2aWNlX3R5cGVfaWQiOjMsInJvbGVzIjoiQU5PTklNTyJ9.CxsRngyK_nO4sJ0CIk8KTvT5wajMlddceH2dgNVJCyZjSj6LnahPar4deHSfr1In"


class APIWorker(QThread):
    """Worker thread para peticiones API no bloqueantes"""
    data_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, url, headers):
        super().__init__()
        self.url = url
        self.headers = headers
    
    def run(self):
        try:
            resp = requests.get(self.url, headers=self.headers, timeout=15)
            if resp.status_code == 200:
                self.data_ready.emit(resp.json())
            else:
                self.error_occurred.emit(f"Error HTTP {resp.status_code}")
        except Exception as e:
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Configuración de ventana
        self.setWindowTitle("EMT Palma - Consulta de Líneas y Paradas")
        self.setMinimumSize(600, 400)
        
        # Datos y estado
        self.line_colors = {}
        self.lines_data = []
        self.current_line_data = None
        self.map_window = None
        self.api_worker = None
        
        # Configuración inicial
        self.setup_first_tab()
        self.setup_second_tab()
        
        # Cargar datos iniciales
        self.load_initial_data()

    def setup_first_tab(self):
        """Configuración de la primera pestaña (funcionalidad existente)"""
        self.ui.pushButton.clicked.connect(self.on_fetch_pressed)
        self.ui.pushButton.setText("🔍 Buscar")
        self.ui.label.setText("🚌 EMT Palma - Consulta de Paradas")
        self.ui.label_2.setText("📋 Historial de búsquedas:")
        
        # Configurar botones de historial
        self.recent_stops = []
        self.grid_buttons = [
            self.ui.pushButton_2, self.ui.pushButton_3, self.ui.pushButton_4,
            self.ui.pushButton_5, self.ui.pushButton_6, self.ui.pushButton_7,
        ]
        
        for button in self.grid_buttons:
            button.setText("-")
            button.setEnabled(False)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:enabled:hover {
                    background-color: #007cba;
                    color: white;
                }
            """)

        # Configurar área de resultados
        contents = self.ui.scrollArea.widget()
        if contents.layout() is None:
            self.results_layout = QVBoxLayout(contents)
            contents.setLayout(self.results_layout)
        else:
            self.results_layout = contents.layout()
            
        self.ui.scrollArea.setMinimumSize(400, 200)
        self.ui.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def setup_second_tab(self):
        """Configuración de la segunda pestaña"""
        # Configurar etiquetas
        self.ui.label_3.setText("🚌 Líneas EMT")
        self.ui.label_4.setText("🎯 Direcciones y Sublíneas")
        
        # Configurar primer scroll area (líneas)
        lines_contents = self.ui.scrollArea_2.widget()
        if lines_contents.layout() is None:
            self.lines_layout = QVBoxLayout(lines_contents)
            lines_contents.setLayout(self.lines_layout)
        else:
            self.lines_layout = lines_contents.layout()
            
        # Configurar segundo scroll area (direcciones)
        sublines_contents = self.ui.scrollArea_3.widget()
        if sublines_contents.layout() is None:
            self.sublines_layout = QVBoxLayout(sublines_contents)
            sublines_contents.setLayout(self.sublines_layout)
        else:
            self.sublines_layout = sublines_contents.layout()

    def load_initial_data(self):
        """Cargar datos iniciales (colores y líneas)"""
        self._show_lines_message("🔄 Cargando líneas EMT...")
        
        headers = {
            "Authorization": TOKEN,
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        
        # Usar worker thread para no bloquear UI
        self.api_worker = APIWorker(
            "https://www.emtpalma.cat/maas/api/v1/agency/lines/",
            headers
        )
        self.api_worker.data_ready.connect(self.on_lines_loaded)
        self.api_worker.error_occurred.connect(self.on_lines_error)
        self.api_worker.start()

    @pyqtSlot(object)
    def on_lines_loaded(self, data):
        """Callback cuando se cargan las líneas"""
        try:
            self.lines_data = data
            
            # Procesar colores de líneas
            self.line_colors = {}
            for linea in data:
                code = str(linea.get("code", ""))
                color_hex = linea.get("routeColor")
                if color_hex:
                    color = f"#{color_hex}"
                else:
                    color = "#007cba"  # Color por defecto EMT
                self.line_colors[code] = color
            
            # Mostrar líneas en la interfaz
            self.display_lines()
            
        except Exception as e:
            self.on_lines_error(f"Error procesando datos: {e}")

    @pyqtSlot(str)
    def on_lines_error(self, error_msg):
        """Callback para errores al cargar líneas"""
        self._show_lines_message(f"❌ Error: {error_msg}")
        print(f"Error cargando líneas: {error_msg}")

    def display_lines(self):
        """Mostrar líneas en el primer scroll area"""
        self._clear_lines()
        
        if not self.lines_data:
            self._show_lines_message("❌ No se encontraron líneas")
            return
        
        # Ordenar líneas por código
        sorted_lines = sorted(self.lines_data, key=lambda x: str(x.get("code", "")))
        
        for line in sorted_lines:
            line_code = str(line.get("code", ""))
            line_name = line.get("name", f"Línea {line_code}")
            color = self.line_colors.get(line_code, "#007cba")
            
            # Crear botón de línea
            button = QPushButton(f"🚌 {line_code} - {line_name}")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 6px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {self._darken_color(color)};
                    transform: translateY(-1px);
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color, 0.3)};
                }}
            """)
            
            button.clicked.connect(lambda checked, line_data=line: self.on_line_clicked(line_data))
            self.lines_layout.addWidget(button)
        
        # Mensaje informativo
        info_label = QLabel(f"✅ {len(sorted_lines)} líneas cargadas")
        info_label.setStyleSheet("color: #28a745; font-weight: bold; padding: 8px;")
        self.lines_layout.addWidget(info_label)

    def on_line_clicked(self, line_data):
        """Manejar clic en una línea"""
        self.current_line_data = line_data
        line_code = str(line_data.get("code", ""))
        line_name = line_data.get("name", f"Línea {line_code}")
        
        self._show_sublines_message(f"🔄 Cargando direcciones de {line_name}...")
        
        # Cargar direcciones de la línea
        url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_code}/directions"
        headers = {
            "Authorization": TOKEN,
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        
        # Usar worker thread
        if self.api_worker and self.api_worker.isRunning():
            self.api_worker.terminate()
            
        self.api_worker = APIWorker(url, headers)
        self.api_worker.data_ready.connect(
            lambda data: self.on_directions_loaded(data, line_code, line_name)
        )
        self.api_worker.error_occurred.connect(
            lambda error: self._show_sublines_message(f"❌ Error: {error}")
        )
        self.api_worker.start()

    def on_directions_loaded(self, directions_data, line_code, line_name):
        """Callback cuando se cargan las direcciones"""
        self._clear_sublines()
        
        if not directions_data:
            self._show_sublines_message("❌ No se encontraron direcciones")
            return
        
        line_color = self.line_colors.get(line_code, "#007cba")
        
        # Título
        title_label = QLabel(f"📍 Direcciones de {line_name}")
        title_label.setStyleSheet(f"""
            QLabel {{
                background-color: {line_color};
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
                margin-bottom: 4px;
            }}
        """)
        self.sublines_layout.addWidget(title_label)
        
        # Botones de direcciones
        for direction in directions_data:
            direction_name = direction.get("name", "Dirección desconocida")
            direction_id = direction.get("id", "")
            
            button = QPushButton(f"🎯 {direction_name}")
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self._lighten_color(line_color)};
                    color: #333;
                    border: 2px solid {line_color};
                    padding: 10px;
                    text-align: left;
                    margin: 3px;
                    border-radius: 6px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background-color: {line_color};
                    color: white;
                    transform: translateX(5px);
                }}
            """)
            
            button.clicked.connect(
                lambda checked, dir_data=direction: self.on_direction_clicked(dir_data)
            )
            self.sublines_layout.addWidget(button)

    def on_direction_clicked(self, direction_data):
        """Manejar clic en una dirección - abrir mapa"""
        if not self.current_line_data:
            return
            
        line_code = str(self.current_line_data.get("code", ""))
        line_name = self.current_line_data.get("name", f"Línea {line_code}")
        direction_id = direction_data.get("id", "")
        direction_name = direction_data.get("name", "")
        line_color = self.line_colors.get(line_code, "#007cba")
        
        # Mostrar mensaje de carga
        QMessageBox.information(
            self, 
            "Cargando Mapa", 
            f"Cargando mapa de {line_name}\nDirección: {direction_name}\n\nEsto puede tardar unos segundos..."
        )
        
        # Cargar ruta y mostrar mapa
        self.load_route_and_show_map(line_code, direction_id, line_color, line_name, direction_name)

    def load_route_and_show_map(self, line_code, direction_id, line_color, line_name, direction_name):
        """Cargar datos de ruta y mostrar mapa"""
        try:
            # URL para obtener paradas de la dirección
            stops_url = f"https://www.emtpalma.cat/maas/api/v1/agency/lines/{line_code}/directions/{direction_id}/stops"
            headers = {
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
            
            print(f"Cargando paradas desde: {stops_url}")
            
            resp = requests.get(stops_url, headers=headers, timeout=15)
            if resp.status_code != 200:
                QMessageBox.warning(self, "Error", f"Error al cargar paradas: HTTP {resp.status_code}")
                return
                
            stops_data = resp.json()
            print(f"Paradas recibidas: {len(stops_data)}")
            
            if not stops_data:
                QMessageBox.information(self, "Sin Datos", "No se encontraron paradas para esta dirección")
                return
            
            # Crear o mostrar ventana del mapa
            if self.map_window is None:
                self.map_window = MapWindow()
                self.map_window.stop_clicked.connect(self.on_map_stop_clicked)
            
            # Configurar mapa
            self.map_window.clear_map()
            self.map_window.draw_route(line_color, stops_data)
            self.map_window.draw_stops(stops_data)
            
            # Actualizar título del mapa
            map_title = f"Mapa EMT - {line_name}: {direction_name}"
            self.map_window.setWindowTitle(map_title)
            
            # Mostrar ventana del mapa
            self.map_window.show()
            self.map_window.raise_()
            self.map_window.activateWindow()
            
        except Exception as e:
            error_msg = f"Error al cargar ruta: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    @pyqtSlot(str)
    def on_map_stop_clicked(self, stop_number):
        """Manejar clic en parada desde el mapa"""
        print(f"Parada clickeada desde mapa: {stop_number}")
        
        # Cambiar a la primera pestaña
        self.ui.tabWidget.setCurrentIndex(0)
        
        # Buscar la parada
        self.ui.lineEdit.setText(str(stop_number))
        self.buscar(str(stop_number))
        
        # Mostrar mensaje de confirmación
        QMessageBox.information(
            self, 
            "Parada Seleccionada", 
            f"Consultando horarios de la parada {stop_number}"
        )

    # Métodos de la primera pestaña (funcionalidad existente)
    def on_fetch_pressed(self):
        """Manejar búsqueda de parada"""
        stop_text = self.ui.lineEdit.text().strip()
        if not stop_text:
            self._show_message("⚠️ Introduce el número de parada.")
            return

        # Actualizar historial
        if stop_text in self.recent_stops:
            self.recent_stops.remove(stop_text)
        self.recent_stops.insert(0, stop_text)
        self.recent_stops = self.recent_stops[:len(self.grid_buttons)]

        # Actualizar botones de historial
        for i, button in enumerate(self.grid_buttons):
            if i < len(self.recent_stops):
                button.setText(self.recent_stops[i])
                button.setEnabled(True)
                try:
                    button.clicked.disconnect()
                except Exception:
                    pass
                button.clicked.connect(
                    lambda checked, s=self.recent_stops[i]: self.buscar(s)
                )
            else:
                button.setText("-")
                button.setEnabled(False)

        self.buscar(stop_text)

    def buscar(self, stop_text):
        """Buscar horarios de una parada"""
        self.ui.lineEdit.setText(stop_text)
        url = f"https://www.emtpalma.cat/maas/api/v1/agency/stops/{stop_text}/timestr"
        
        self._clear_results()
        self._show_message("🔄 Cargando horarios...")
        
        try:
            headers = {
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
            
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                self._show_message(f"❌ Error HTTP {resp.status_code}")
                return

            data = resp.json()
            self._clear_results()
            
            if not data:
                self._show_message(f"ℹ️ No hay información disponible para la parada {stop_text}")
                return
            
            # Título
            title_label = QLabel(f"🚌 Parada {stop_text} - Próximos autobuses")
            title_label.setStyleSheet("""
                QLabel {
                    background-color: #007cba;
                    color: white;
                    padding: 8px;
                    font-weight: bold;
                    border-radius: 4px;
                    margin-bottom: 8px;
                }
            """)
            self.results_layout.addWidget(title_label)
            
            # Procesar datos de vehículos
            for entry in data:
                line = entry.get("lineCode", "—")
                vehicles = entry.get("vehicles", [])
                
                if not vehicles:
                    continue
                
                for v in vehicles:
                    seconds = v.get("seconds")
                    destination = v.get("destination", "")
                    at_stop = v.get("atStop", False)
                    arriving = v.get("arriving", False)

                    # Calcular tiempo de llegada
                    if at_stop:
                        minutes_text = "🚌 EN PARADA"
                        status_color = "#28a745"
                    elif arriving:
                        minutes_text = "🔄 LLEGANDO"
                        status_color = "#ffc107"
                    elif isinstance(seconds, (int, float)) and seconds > 0:
                        minutes = math.ceil(seconds / 60)
                        minutes_text = f"⏱️ {minutes} min"
                        status_color = "#007cba"
                    else:
                        minutes_text = "❓ Sin datos"
                        status_color = "#6c757d"

                    # Crear etiqueta de resultado
                    line_color = self.line_colors.get(line, "#007cba")
                    
                    result_label = QLabel(f"Línea {line} → {destination}")
                    result_label.setStyleSheet(f"""
                        QLabel {{
                            background-color: {line_color};
                            color: white;
                            padding: 6px 10px;
                            margin: 2px;
                            border-radius: 4px;
                            font-weight: bold;
                        }}
                    """)
                    
                    time_label = QLabel(minutes_text)
                    time_label.setStyleSheet(f"""
                        QLabel {{
                            background-color: {status_color};
                            color: white;
                            padding: 4px 8px;
                            margin: 2px;
                            border-radius: 3px;
                            font-size: 11px;
                            font-weight: bold;
                        }}
                    """)
                    
                    self.results_layout.addWidget(result_label)
                    self.results_layout.addWidget(time_label)
                    
        except Exception as e:
            self._show_message(f"❌ Error al consultar parada: {e}")

    # Métodos auxiliares para UI
    def _clear_results(self):
        """Limpiar resultados de búsqueda"""
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _show_message(self, text):
        """Mostrar mensaje en área de resultados"""
        self._clear_results()
        lbl = QLabel(text)
        lbl.setStyleSheet("padding: 10px; font-size: 12px;")
        self.results_layout.addWidget(lbl)

    def _clear_lines(self):
        """Limpiar lista de líneas"""
        while self.lines_layout.count():
            item = self.lines_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _show_lines_message(self, text):
        """Mostrar mensaje en área de líneas"""
        self._clear_lines()
        lbl = QLabel(text)
        lbl.setStyleSheet("padding: 15px; font-size: 12px; text-align: center;")
        self.lines_layout.addWidget(lbl)

    def _clear_sublines(self):
        """Limpiar lista de direcciones"""
        while self.sublines_layout.count():
            item = self.sublines_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _show_sublines_message(self, text):
        """Mostrar mensaje en área de direcciones"""
        self._clear_sublines()
        lbl = QLabel(text)
        lbl.setStyleSheet("padding: 15px; font-size: 12px; text-align: center;")
        self.sublines_layout.addWidget(lbl)

    def _darken_color(self, color, factor=0.2):
        """Oscurecer un color"""
        if not color.startswith('#'):
            return "#333333"
        try:
            color = color[1:]
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = max(0, int(r * (1 - factor)))
            g = max(0, int(g * (1 - factor)))
            b = max(0, int(b * (1 - factor)))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#333333"

    def _lighten_color(self, color, factor=0.6):
        """Aclarar un color"""
        if not color.startswith('#'):
            return "#cccccc"
        try:
            color = color[1:]
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#cccccc"

    def closeEvent(self, event):
        """Limpiar al cerrar aplicación"""
        if self.map_window:
            self.map_window.close()
        if self.api_worker and self.api_worker.isRunning():
            self.api_worker.terminate()
            self.api_worker.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("EMT Palma")
    app.setApplicationVersion("2.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())