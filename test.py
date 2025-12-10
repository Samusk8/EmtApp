import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

# Importamos la clase MapWindow del archivo anterior
from mapView import MapWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ventana Principal")
        self.setGeometry(100, 100, 300, 200)

        # Layout
        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Botón
        self.button = QPushButton("Abrir Mapa")
        layout.addWidget(self.button)

        # Acción del botón
        self.button.clicked.connect(self.open_map)

        # Para no recrear la ventana siempre
        self.map_window = None

    def open_map(self):
        if self.map_window is None:
            # Coordenadas: Palma de Mallorca
            latitude = 39.57
            longitude = 2.65

            self.map_window = MapWindow(latitude, longitude)

        self.map_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
