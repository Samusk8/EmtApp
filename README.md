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

#### Pestaña 1: Paso por Parada
- ✅ Consulta de horarios en tiempo real por número de parada
- ✅ Historial de paradas consultadas (botones de acceso rápido)
- ✅ Visualización de líneas con colores oficiales EMT
- ✅ Información de tiempo de llegada (en parada, llegando, X minutos)

#### Pestaña 2: Consulta de Líneas
- ✅ Lista completa de líneas EMT con colores oficiales
- ✅ Consulta de direcciones/sublíneas por línea
- ✅ **Mapa interactivo** con ruta y paradas
- ✅ **Comunicación por señales** entre mapa y aplicación principal
- ✅ Clic en parada del mapa → automáticamente consulta horarios

### Características Técnicas

#### Arquitectura
- **Aplicación principal**: `app_final.py`
- **Paquete de mapa**: `map_package_enhanced.py` (reutilizable)
- **Interfaz UI**: `mainWindowUi2.py` (generada desde Qt Designer)
- **Comunicación**: Señales PyQt6 entre ventanas

#### Señales Implementadas
- **Entrada al mapa**:
  - `draw_route(color, stops_data)` - Dibujar ruta con color oficial
  - `draw_stops(stops_data)` - Marcar paradas en el mapa
  - `clear_map()` - Limpiar mapa
- **Salida del mapa**:
  - `stop_clicked(stop_number)` - Parada clickeada en el mapa

#### Tecnologías
- **PyQt6** - Interfaz gráfica y señales
- **PyQt6-WebEngine** - Visualización de mapas web
- **Folium** - Generación de mapas interactivos
- **Requests** - Comunicación con API EMT

## Instalación

### 1. Requisitos del Sistema
```bash
Python 3.8+
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install PyQt6==6.7.1
pip install PyQt6-WebEngine==6.7.0
pip install folium==0.17.0
pip install requests==2.31.0
```

### 3. Estructura de Archivos
```
proyecto/
├── app_final.py                 # Aplicación principal
├── map_package_enhanced.py      # Paquete de mapa
├── requirements.txt             # Dependencias
├── View/
│   └── mainWindowUi2.py        # Interfaz generada
└── README.md                   # Este archivo
```

## Uso

### Ejecutar la Aplicación
```bash
python app_final.py
```

### Pestaña 1: Paso por Parada
1. Introduce el número de parada en el campo de texto
2. Haz clic en "🔍 Buscar"
3. Ve los horarios en tiempo real
4. Usa los botones de historial para acceso rápido

### Pestaña 2: Consulta de Líneas
1. **Seleccionar línea**: Haz clic en cualquier línea del primer panel
2. **Elegir dirección**: Aparecerán las direcciones en el segundo panel
3. **Ver mapa**: Haz clic en una dirección para abrir el mapa interactivo
4. **Consultar parada**: En el mapa, haz clic en cualquier parada para ver sus horarios

### Funciones del Mapa
- **Navegación**: Zoom y desplazamiento con ratón
- **Paradas**: Marcadores azules (inicio: verde, final: rojo)
- **Ruta**: Línea con color oficial de la línea EMT
- **Interacción**: Clic en parada → consulta automática de horarios
- **Controles**: Botones para centrar, limpiar y cerrar

## API EMT Palma

La aplicación utiliza la API oficial de EMT Palma:

### Endpoints Utilizados
- `GET /agency/lines/` - Lista de líneas y colores
- `GET /agency/lines/{line}/directions` - Direcciones de una línea
- `GET /agency/lines/{line}/directions/{direction}/stops` - Paradas de una dirección
- `GET /agency/stops/{stop}/timestr` - Horarios de una parada

### Autenticación
La aplicación incluye un token de acceso válido. Si expira, será necesario obtener uno nuevo desde el portal de desarrolladores de EMT Palma.

## Desarrollo

### Estructura del Código

#### Clase Principal: `MainWindow`
- Hereda de `QMainWindow`
- Gestiona ambas pestañas
- Maneja comunicación con API
- Controla ventana de mapa

#### Paquete de Mapa: `MapWindow`
- Ventana independiente y reutilizable
- Comunicación por señales PyQt6
- Mapas interactivos con Folium
- Integración WebEngine

#### Worker Threads
- `APIWorker` - Peticiones HTTP no bloqueantes
- Evita congelación de la interfaz
- Manejo de errores robusto

### Señales y Slots

```python
# Señal del mapa al hacer clic en parada
map_window.stop_clicked.connect(self.on_map_stop_clicked)

# Slot en aplicación principal
@pyqtSlot(str)
def on_map_stop_clicked(self, stop_number):
    # Cambiar a pestaña 1 y buscar parada
    self.ui.tabWidget.setCurrentIndex(0)
    self.buscar(str(stop_number))
```

### Personalización de Colores
Los colores de las líneas se obtienen automáticamente de la API EMT y se aplican consistentemente en:
- Botones de líneas
- Rutas en el mapa
- Etiquetas de resultados

## Solución de Problemas

### Error de Conexión API
- Verificar conexión a internet
- Comprobar validez del token de acceso
- Revisar logs de consola para detalles

### Mapa No Carga
- Verificar instalación de PyQt6-WebEngine
- Comprobar permisos de archivos temporales
- Revisar logs de JavaScript en consola

### Rendimiento Lento
- Las peticiones API se ejecutan en threads separados
- El mapa se genera bajo demanda
- Cerrar ventanas de mapa no utilizadas

## Licencia

Proyecto educativo para la asignatura de desarrollo de interfaces.

## Créditos

- **API**: EMT Palma (Empresa Municipal de Transports de Palma)
- **Mapas**: OpenStreetMap
- **Framework**: PyQt6
- **Visualización**: Folium
## Developers
<a href="https://github.com/Samusk8">
  <img src="https://img.shields.io/badge/Profile-Samusk8-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>
<a href="https://chatgpt.com">
<img src="https://img.shields.io/badge/CarlosGPT-(ChatGPT)-0A7CCC?style=for-the-badge&logo=openai&logoColor=white"/>
</a>

