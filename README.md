<!--# EmtApp
- py -m venv venv
- ./venv/Scripts/activate
- pip install pyqt6
- pip install pyqt6-tools
- python -m pip install --upgrade pip setuptools wheel
- pyuic6
- py Controller/app.py-->

# 🚍 EMT Palma – Bus Arrival Times App

A desktop application developed with Python and PyQt6 that allows users to check the next buses arriving at a Palma EMT bus stop in real time. The user enters the stop number, the application makes a request to the official API, and displays the lines, destinations, and estimated arrival time of each bus.

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/bf/Logo_EMT_Palma_2019.png" alt="Logo EMT Palma" width="200">
</p>

---

## 📌 Usages

This app allows EMT Palma users to quickly and easily find out **when the next bus will arrive at any stop in the city**.

There's no need to access the official website: the program connects directly to the EMT Palma API, processes the information, and displays it clearly in the interface.

---

## 🏷️ Main Features

✅ Real-time arrival times by entering the stop number

✅ Direct query to the official EMT Palma API

✅ Simple graphical interface using PyQt6

✅ Clean results in a dynamic ScrollArea

✅ No threading required, as requested

---


## ⚙️ Get Started

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/EmtApp.git

# 2. Entrar al proyecto
cd EmtApp

# 3. Crear un entorno virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate   # En Windows

# 4. Instalar dependencias
pip install -r requirements.txt
pip install requests

# 5. Ejecutar la aplicación
py Controller/app.py
```
## Developers
<a href="https://github.com/Samusk8">
  <img src="https://img.shields.io/badge/Profile-Samusk8-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>
<a href="https://chatgpt.com">
<img src="https://img.shields.io/badge/CarlosGPT-(ChatGPT)-0A7CCC?style=for-the-badge&logo=openai&logoColor=white"/>
</a>

