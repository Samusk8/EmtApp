# map_window.py
import os
import tempfile
import folium
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import pyqtSignal, QUrl

class MapWindow(QMainWindow):
    # Señales: entrada (draw/clear) y salida (stop clicked)
    drawRequested = pyqtSignal(dict)   # espera {'coords': [(lat,lng),...], 'stops': [{'id':..., 'lat':..., 'lng':..., 'name':...}], 'color': '#rrggbb'}
    clearRequested = pyqtSignal()
    stopClicked = pyqtSignal(str)      # emite id de parada como string

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mapa de línea")
        self.resize(900, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.view = QWebEngineView()
        layout.addWidget(self.view)

        # temp file
        self._tmp_html = os.path.join(tempfile.gettempdir(), "emt_map.html")

        # conexiones
        self.drawRequested.connect(self.on_draw_requested)
        self.clearRequested.connect(self.on_clear_requested)

        # detectar pulsación de marcador mediante cambio de URL "emt://stop/<id>"
        self.view.urlChanged.connect(self._on_url_changed)

        self.generate_empty_map()

    def generate_empty_map(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        map_path = os.path.join(base_path, "map_temp.html")
        m = folium.Map(location=(39.5696,2.6502), zoom_start=13)
        m.save(map_path)
        self.view.load(QUrl.fromLocalFile(map_path))

    def _on_url_changed(self, qurl: QUrl):
        scheme = qurl.scheme()
        if scheme == "emt":
            # url form emt://stop/12345
            parts = qurl.toString().split("/")
            if len(parts) >= 3 and parts[1] == "" and parts[2].startswith("stop"):
                # parts like ['emt:', '', 'stop', '12345'] depending; safer parse:
                # parse the last chunk as id
                stop_id = parts[-1]
                self.stopClicked.emit(stop_id)

    def on_draw_requested(self, payload: dict):
        """Payload: {'coords': [(lat,lng),...], 'stops':[{'id':..,'lat':..,'lng':..,'name':..}], 'color':'#rrggbb'}"""
        coords = payload.get("coords", [])
        stops = payload.get("stops", [])
        color = payload.get("color", "#FF0000")

        if coords:
            # center map on middle coordinate
            mid = coords[len(coords)//2]
            m = folium.Map(location=mid, zoom_start=13)
        elif stops:
            mid = (stops[0]['lat'], stops[0]['lng'])
            m = folium.Map(location=mid, zoom_start=13)
        else:
            m = folium.Map(location=(39.5696,2.6502), zoom_start=13)

        # dibujar ruta si hay coords
        if coords:
            folium.PolyLine(locations=coords, color=color, weight=6, opacity=0.9).add_to(m)

        # añadir stops como marcadores; cuando se pulsen, navegamos a emt://stop/<id>
        for s in stops:
            sid = str(s.get("id", ""))
            lat = s.get("lat")
            lng = s.get("lng")
            name = s.get("name", "")
            if lat is None or lng is None:
                continue
            # popup + onclick JS to change location to emt scheme
            js = f"function(){'{'}window.location.href='emt://stop/{sid}';{'}'}"
            folium.Marker(
                location=(lat, lng),
                tooltip=name,
                popup=name,
                icon=folium.Icon(icon="bus", prefix="fa")
            ).add_to(m).add_child(folium.Html(f"<a href='#' onclick=\"window.location.href='emt://stop/{sid}'\">Seleccionar parada</a>", script=True))

        # guardar HTML y cargarlo
        m.save(self._tmp_html)
        self.view.load(QUrl.fromLocalFile(self._tmp_html))

    def on_clear_requested(self):
        # cargar mapa vacío
        m = folium.Map(location=(39.5696,2.6502), zoom_start=13)
        m.save(self._tmp_html)
        self.view.load(QUrl.fromLocalFile(self._tmp_html))
