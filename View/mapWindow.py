import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import folium

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa de prueba")
        self.setGeometry(100, 100, 800, 600)
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)
        self.map_file = "mapa_prueba.html"

    def draw_sample_map(self):
        # Crear mapa con folium
        m = folium.Map(location=[39.57, 2.65], zoom_start=13)
        folium.Marker([39.57, 2.65], tooltip="Palma de Mallorca").add_to(m)
        
        # Guardar el HTML primero
        m.save(self.map_file)
        
        # Cargar en el WebEngineView usando QUrl
        self.webview.setUrl(QUrl.fromLocalFile(os.path.abspath(self.map_file)))

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

    def open_map(self):
        if not self.map_window:
            self.map_window = MapWindow()
        self.map_window.show()
        QTimer.singleShot(100, self.map_window.draw_sample_map)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
