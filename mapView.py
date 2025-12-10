import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView
import folium
from folium import plugins

def create_map(latitude, longitude, zoom_start=12):
    """
    Create an interactive folium map with marker, circle, fullscreen button 
    and locate control.
    """
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    folium.Marker(
        [latitude, longitude],
        popup='Selected Location',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    folium.Circle(
        location=[latitude, longitude],
        radius=1000,
        color='crimson',
        fill=True
    ).add_to(m)

    plugins.Fullscreen().add_to(m)
    plugins.LocateControl().add_to(m)

    return m


class MapWindow(QMainWindow):
    """
    Standalone MapView window.
    Pass latitude/longitude to display a folium map.
    """

    def __init__(self, latitude, longitude, zoom_start=12):
        super().__init__()

        self.map = create_map(latitude, longitude, zoom_start)

        # Web browser widget
        self.browser = QWebEngineView()

        # Load map HTML directly (this avoids blank window issues)
        html = self.map.get_root().render()
        self.browser.setHtml(html)

        self.setCentralWidget(self.browser)
        self.setWindowTitle("Mapa EMT — PyQt6 + Folium")
        self.resize(900, 700)



# Test if run standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Example coords
    latitude = 39.570
    longitude = 2.650

    window = MapWindow(latitude, longitude)
    window.show()

    sys.exit(app.exec())
