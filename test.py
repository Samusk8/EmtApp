import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import folium

class MapWindow(QMainWindow):
    def __init__(self, map_file):
        super().__init__()
        self.setWindowTitle("Mapa de prueba")
        self.setGeometry(100, 100, 800, 600)
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)
        self.map_file = map_file

    def load_map(self):
        # Cargar el HTML del mapa en el WebEngineView
        file_path = os.path.abspath(self.map_file)
        self.webview.setUrl(QUrl.fromLocalFile(file_path))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Mapa")
        self.setGeometry(50, 50, 300, 200)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.button = QPushButton("Abrir mapa")
        layout.addWidget(self.button)

        self.button.clicked.connect(self.open_map)
        self.map_window = None

        # Generamos el HTML del mapa solo una vez
        self.map_file = "C:/Users/Alumne/Documents/GitHub/EmtApp/mapa_test.html"
        self.generate_map_html()

    def generate_map_html(self):
        # Crear mapa con folium y guardarlo en HTML
        m = folium.Map(location=[39.57, 2.65], zoom_start=13)
        folium.Marker([39.57, 2.65], tooltip="Palma de Mallorca").add_to(m)
        m.save(self.map_file)

    def open_map(self):
        if self.map_window is None:
            self.map_window = MapWindow(self.map_file)
        self.map_window.load_map()
        self.map_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
