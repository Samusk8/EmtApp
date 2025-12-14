from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
import io

class MapWindow(QMainWindow):
    stop_clicked = pyqtSignal(str)  

    def __init__(self, latitude=39.57, longitude=2.65, zoom_start=13):
        super().__init__()
        self.setWindowTitle("Mapa EMT")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.latitude = latitude
        self.longitude = longitude
        self.zoom_start = zoom_start
        self.fmap = folium.Map(location=[self.latitude, self.longitude], zoom_start=self.zoom_start)

        self._update_map()

    def _update_map(self):
        data = io.BytesIO()
        self.fmap.save(data, close_file=False)
        self.web_view.setHtml(data.getvalue().decode())

    def clear_map(self):
        self.fmap = folium.Map(location=[self.latitude, self.longitude], zoom_start=self.zoom_start)
        self._update_map()

    def draw_route(self, line_color, stops_data):
        if not stops_data:
            return
        coords = [(stop["stopLat"], stop["stopLon"]) for stop in stops_data]
        folium.PolyLine(coords, color=line_color, weight=5).add_to(self.fmap)
        self._update_map()

    def draw_stops(self, stops_data):
        if not stops_data:
            return

        for stop in stops_data:
            lat = stop["stopLat"]
            lon = stop["stopLon"]
            stop_number = stop["stopCode"]
            stop_name = stop["stopName"]

            popup_html = f"""
            <b>{stop_name}</b><br>
            <button onclick="stopClicked('{stop_number}')">Seleccionar</button>
            """
            folium.Marker(
                location=(lat, lon),
                popup=popup_html,
                tooltip=stop_name,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(self.fmap)

        
        self.fmap.get_root().html.add_child(folium.Element("""
            <script>
            function stopClicked(stopNumber) {
                alert(stopNumber); 
            }
            </script>
        """))

        self._update_map()
