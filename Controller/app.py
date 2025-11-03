
import sys
import os
import math
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout
from View.main_Window_ui import Ui_MainWindow


TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzM4NCJ9.eyJzdWIiOiI3ODQ1ODUiLCJpYXQiOjE3NjE1NjkzNzcsImV4cCI6MzMzOTQ0OTM3NywidXNlcm5hbWUiOiIxNzYxNTY5Mzc3NTE0M0ZLMUlJSVo0MEo2V0tCNklSNlUiLCJ0b2tlbl9kZXZpY2UiOiJmNTJiMjdiZjQyMjNjNTdhYWUxNDg4ZjU3OGE2OTdjNDk3OWIzNTNlZjZjODEyZmQwMTM3NGNlNGY2ODE5OWE1IiwiZGV2aWNlX3R5cGVfaWQiOjMsInJvbGVzIjoiQU5PTklNTyJ9.CxsRngyK_nO4sJ0CIk8KTvT5wajMlddceH2dgNVJCyZjSj6LnahPar4deHSfr1In"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Preparar layout dentro del scroll area
        contents = self.ui.scrollArea.widget()
        if contents.layout() is None:
            self.results_layout = QVBoxLayout(contents)
            contents.setLayout(self.results_layout)
        else:
            self.results_layout = contents.layout()

        self.ui.pushButton.clicked.connect(self.on_fetch_pressed)

    def on_fetch_pressed(self):
        stop_text = self.ui.lineEdit.text().strip()
        if not stop_text:
            self._show_message("Introduce el número de parada.")
            return

        url = f"https://www.emtpalma.cat/maas/api/v1/agency/stops/{stop_text}/timestr"

        self._clear_results()
        self._show_message("Cargando...")

        try:
            headers = {
                "Authorization": TOKEN,
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                self._show_message(f"Error HTTP {resp.status_code}")
                return

            data = resp.json()

            self._clear_results()

            if not data:
                self._show_message("No hay vehículos próximos.")
                return

            for entry in data:
                line = entry.get("lineCode", "—")
                vehicles = entry.get("vehicles", [])
                if not vehicles:
                    lbl = QLabel(f"Línea {line}: sin vehículos próximos")
                    self.results_layout.addWidget(lbl)
                    continue

                for v in vehicles:
                    seconds = v.get("seconds")
                    destination = v.get("destination", "")
                    meters = v.get("meters", None)
                    at_stop = v.get("atStop", False)
                    arriving = v.get("arriving", False)

                    if at_stop:
                        minutes_text = "en parada"
                    elif arriving:
                        minutes_text = "llegando"
                    elif isinstance(seconds, (int, float)):
                        minutes_text = f"{math.ceil(seconds / 60)} min"
                    else:
                        minutes_text = "—"

                    meters_text = f" · {meters} m" if meters is not None else ""
                    text = f"L{line} — {minutes_text} — {destination}{meters_text}"
                    lbl = QLabel(text)
                    self.results_layout.addWidget(lbl)

        except Exception as e:
            self._show_message(f"Error al pedir datos: {e}")

    def _clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _show_message(self, text):
        self._clear_results()
        lbl = QLabel(text)
        self.results_layout.addWidget(lbl)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
