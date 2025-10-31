import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow
from View.main_Window_ui import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Crear la UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  

        # Aquí puedes conectar botones, por ejemplo:
        # self.ui.pushButton.clicked.connect(self.on_button_click)

    # Ejemplo de función para un botón
    def on_button_click(self):
        print("Botón presionado")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  
    window.show()          
    sys.exit(app.exec())   
