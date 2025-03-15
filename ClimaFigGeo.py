import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
import requests
from dotenv import load_dotenv
import os

class Clima:
    def __init__(self):
        load_dotenv()
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.api_key = os.getenv('API_KEY')

    def consulta_ciudad(self, ciudad):
        params = {
            'q': ciudad,
            'appid': self.api_key,
            'units': 'metric'
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def extrae_relevantes(self, ciudad):
        weather_data = self.consulta_ciudad(ciudad)
        return {
            'ciudad': weather_data['name'],
            'temperatura': weather_data['main']['temp'],
            'icono': weather_data['weather'][0]['icon'],
            'description': weather_data['weather'][0]['description']
        }

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(800, 800)
        canvas.fill(Qt.GlobalColor.white)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.mostrar_clima('Tokio')  # Puedes cambiar 'Toluca' por la ciudad que desees

    def mostrar_clima(self, ciudad):
        c = Clima()
        clima = c.extrae_relevantes(ciudad)
        self.setWindowTitle(f"Clima en {clima['ciudad']}: {clima['temperatura']}°C, {clima['description']}")
        self.dibuja_figura_clima(clima['description'])

    def dibuja_figura_clima(self, description):
        canvas = self.label.pixmap()
        painter = QtGui.QPainter(canvas)
        
        if 'clear' in description.lower():
            painter.setBrush(QtGui.QBrush(Qt.GlobalColor.yellow))
            painter.drawEllipse(100, 100, 100, 100)  # Círculo amarillo para clima soleado
        elif 'clouds' in description.lower():
            painter.setBrush(QtGui.QBrush(Qt.GlobalColor.gray))
            painter.drawRect(250, 100, 100, 100)  # Cuadrado gris para clima despejado
        elif 'rain' in description.lower():
            painter.setBrush(QtGui.QBrush(Qt.GlobalColor.blue))
            painter.drawPolygon(QtGui.QPolygon([
                QtCore.QPoint(400, 200),
                QtCore.QPoint(450, 100),
                QtCore.QPoint(500, 200)
            ]))  # Triángulo azul para días lluviosos
        else:
            print("Clima no reconocido: {}".format(description))
        
        painter.end()
        self.label.setPixmap(canvas)

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
