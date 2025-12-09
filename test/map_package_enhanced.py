"""
Versión mejorada del paquete de mapa con mejor comunicación JavaScript-Python
"""

import sys
import folium
import tempfile
import os
import json
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, 
                            QHBoxLayout, QLabel, QApplication)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import pyqtSignal, QUrl, QObject, pyqtSlot
from PyQt6.QtGui import QIcon


class MapBridge(QObject):
    """Puente para comunicación JavaScript-Python"""
    stop_clicked = pyqtSignal(str)
    
    @pyqtSlot(str)
    def onStopClicked(self, stop_code):
        """Slot para manejar clics en paradas desde JavaScript"""
        print(f"Parada clickeada desde JS: {stop_code}")
        self.stop_clicked.emit(stop_code)


class MapWindow(QMainWindow):
    # Señales de salida
    stop_clicked = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa EMT Palma - Líneas y Paradas")
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Barra de herramientas
        self._setup_toolbar(layout)
        
        # Vista web para el mapa
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Configurar comunicación JavaScript-Python
        self.bridge = MapBridge()
        self.bridge.stop_clicked.connect(self.stop_clicked.emit)
        
        self.channel = QWebChannel()
        self.channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.channel)
        
        # Inicializar mapa
        self.current_map = None
        self.temp_file = None
        self.stops_data = []
        self.current_line_info = ""
        
        self.clear_map()

    def _setup_toolbar(self, layout):
        """Configurar barra de herramientas"""
        toolbar_layout = QHBoxLayout()
        
        self.info_label = QLabel("Mapa EMT Palma")
        self.info_label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                padding: 8px; 
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        toolbar_layout.addWidget(self.info_label)
        
        toolbar_layout.addStretch()
        
        # Botón para centrar mapa
        center_button = QPushButton("Centrar en Palma")
        center_button.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #007cba;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a87;
            }
        """)
        center_button.clicked.connect(self._center_on_palma)
        toolbar_layout.addWidget(center_button)
        
        # Botón para limpiar mapa
        clear_button = QPushButton("Limpiar Mapa")
        clear_button.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        clear_button.clicked.connect(self.clear_map)
        toolbar_layout.addWidget(clear_button)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        close_button.clicked.connect(self.close)
        toolbar_layout.addWidget(close_button)
        
        layout.addLayout(toolbar_layout)

    def clear_map(self):
        """Limpiar el mapa"""
        self.current_map = folium.Map(
            location=[39.5696, 2.6502],  # Palma de Mallorca
            zoom_start=13,
            tiles='OpenStreetMap'
        )
        
        # Agregar marcador de Palma
        folium.Marker(
            [39.5696, 2.6502],
            popup="Palma de Mallorca",
            tooltip="Centro de Palma",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.current_map)
        
        self.stops_data = []
        self.current_line_info = ""
        self.info_label.setText("Mapa EMT Palma - Selecciona una línea")
        self._update_map_display()

    def _center_on_palma(self):
        """Centrar mapa en Palma"""
        if self.current_map:
            self.current_map.location = [39.5696, 2.6502]
            self.current_map.zoom_start = 13
            self._update_map_display()

    def draw_route(self, color, stops_data):
        """Dibujar ruta en el mapa"""
        if not stops_data or not self.current_map:
            print("No hay datos de paradas o mapa no inicializado")
            return
            
        self.stops_data = stops_data
        
        # Extraer coordenadas válidas
        coordinates = []
        valid_stops = []
        
        for stop in stops_data:
            lat = stop.get('latitude')
            lon = stop.get('longitude')
            
            # Verificar que las coordenadas sean válidas
            if (lat is not None and lon is not None and 
                isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                -90 <= lat <= 90 and -180 <= lon <= 180):
                coordinates.append([lat, lon])
                valid_stops.append(stop)
        
        print(f"Paradas válidas encontradas: {len(valid_stops)} de {len(stops_data)}")
        
        if len(coordinates) < 1:
            print("No hay coordenadas válidas para dibujar la ruta")
            self.info_label.setText("No se encontraron coordenadas válidas para esta línea")
            return
            
        # Dibujar línea de la ruta si hay al menos 2 puntos
        if len(coordinates) >= 2:
            folium.PolyLine(
                coordinates,
                color=color,
                weight=5,
                opacity=0.8,
                popup=f"Ruta de línea (Color: {color})"
            ).add_to(self.current_map)
        
        # Ajustar vista del mapa
        if coordinates:
            try:
                lats = [coord[0] for coord in coordinates]
                lons = [coord[1] for coord in coordinates]
                
                # Calcular bounds con margen
                lat_margin = (max(lats) - min(lats)) * 0.1
                lon_margin = (max(lons) - min(lons)) * 0.1
                
                sw = [min(lats) - lat_margin, min(lons) - lon_margin]
                ne = [max(lats) + lat_margin, max(lons) + lon_margin]
                
                self.current_map.fit_bounds([sw, ne])
            except Exception as e:
                print(f"Error ajustando vista del mapa: {e}")
        
        self._update_map_display()

    def draw_stops(self, stops_data):
        """Dibujar paradas en el mapa"""
        if not stops_data or not self.current_map:
            return
            
        valid_stops_count = 0
        
        for i, stop in enumerate(stops_data):
            lat = stop.get('latitude')
            lon = stop.get('longitude')
            stop_code = stop.get('code', f'stop_{i}')
            stop_name = stop.get('name', 'Parada sin nombre')
            
            # Verificar coordenadas válidas
            if (lat is not None and lon is not None and 
                isinstance(lat, (int, float)) and isinstance(lon, (int, float)) and
                -90 <= lat <= 90 and -180 <= lon <= 180):
                
                valid_stops_count += 1
                
                # HTML del popup con botón funcional
                popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 220px; text-align: center;">
                    <h4 style="margin: 5px 0; color: #007cba;">Parada {stop_code}</h4>
                    <p style="margin: 5px 0; font-size: 12px;">{stop_name}</p>
                    <button onclick="window.bridge.onStopClicked('{stop_code}')" 
                            style="margin: 8px 0; padding: 8px 16px; 
                                   background: #007cba; color: white; 
                                   border: none; border-radius: 4px; 
                                   cursor: pointer; font-size: 12px;
                                   transition: background 0.3s;">
                        📍 Consultar Horarios
                    </button>
                </div>
                """
                
                # Determinar color del marcador según posición
                if i == 0:
                    marker_color = 'green'
                    icon_name = 'play'
                elif i == len(stops_data) - 1:
                    marker_color = 'red' 
                    icon_name = 'stop'
                else:
                    marker_color = 'blue'
                    icon_name = 'bus'
                
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"🚌 Parada {stop_code}: {stop_name}",
                    icon=folium.Icon(
                        color=marker_color, 
                        icon=icon_name, 
                        prefix='fa'
                    )
                ).add_to(self.current_map)
        
        # Actualizar información
        line_info = f"Línea cargada: {valid_stops_count} paradas válidas"
        if valid_stops_count != len(stops_data):
            line_info += f" ({len(stops_data) - valid_stops_count} sin coordenadas)"
        
        self.current_line_info = line_info
        self.info_label.setText(line_info)
        
        self._update_map_display()

    def _update_map_display(self):
        """Actualizar visualización del mapa"""
        if not self.current_map:
            return
            
        # Limpiar archivo temporal anterior
        if self.temp_file:
            try:
                os.unlink(self.temp_file)
            except:
                pass
                
        # Crear nuevo archivo temporal
        fd, self.temp_file = tempfile.mkstemp(suffix='.html')
        
        # Generar HTML del mapa
        map_html = self.current_map._repr_html_()
        
        # Insertar script para comunicación con PyQt
        js_bridge_code = """
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            window.onload = function() {
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.bridge = channel.objects.bridge;
                    console.log("Bridge conectado correctamente");
                });
            }
        </script>
        """
        
        # Insertar el código JavaScript antes del cierre de head
        map_html = map_html.replace('</head>', f'{js_bridge_code}</head>')
        
        # Escribir archivo
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(map_html)
        
        # Cargar en vista web
        self.web_view.load(QUrl.fromLocalFile(self.temp_file))

    def closeEvent(self, event):
        """Limpiar al cerrar"""
        if self.temp_file:
            try:
                os.unlink(self.temp_file)
            except:
                pass
        event.accept()


# Función de utilidad
def create_map_window():
    """Crear nueva ventana de mapa"""
    return MapWindow()


# Demo/Testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Crear ventana de mapa
    map_window = MapWindow()
    
    # Datos de prueba con coordenadas de Palma
    test_stops = [
        {
            'code': '001',
            'name': 'Plaza España',
            'latitude': 39.5696,
            'longitude': 2.6502
        },
        {
            'code': '002', 
            'name': 'Estación Intermodal',
            'latitude': 39.5720,
            'longitude': 2.6520
        },
        {
            'code': '003',
            'name': 'Avenidas',
            'latitude': 39.5750,
            'longitude': 2.6480
        }
    ]
    
    # Conectar señal
    def on_stop_clicked(stop_code):
        print(f"¡Parada {stop_code} clickeada! Cambiando a pestaña de horarios...")
    
    map_window.stop_clicked.connect(on_stop_clicked)
    
    # Mostrar mapa con datos de prueba
    map_window.draw_route("#FF6B35", test_stops)
    map_window.draw_stops(test_stops)
    
    map_window.show()
    sys.exit(app.exec())