import sys
import os
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
import requests
from dotenv import load_dotenv

# Clase para consultar datos del clima
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
        response.raise_for_status()  # Lanza excepción si hay error
        return response.json()

    def extrae_relevantes(self, ciudad):
        weather_data = self.consulta_ciudad(ciudad)
        if 'name' not in weather_data or 'main' not in weather_data:
            raise ValueError("Datos incompletos recibidos desde la API.")
        return {
            'ciudad': weather_data['name'],
            'temperatura': weather_data['main']['temp'],
            'icono': weather_data['weather'][0]['icon'],
            'description': weather_data['weather'][0]['description']
        }

# Función para generar la imagen con Wand

def dibuja(ciudad, datos_clima):
    try:
        # Definir el fondo según el momento del día (día o noche)
        fondo = Color('lightblue') if datos_clima['icono'][-1] == 'd' else Color('darkblue')

        # Ruta para guardar la imagen generada
        ruta_imagen = f"{ciudad}_clima.png"

        with Drawing() as draw:
            draw.stroke_color = Color('black')
            draw.stroke_width = 2

            # Dibujar figura geométrica según la descripción del clima
            if 'clear' in datos_clima['description'].lower():
                draw.fill_color = Color('yellow')  # Círculo amarillo
                draw.circle((200, 150), (250, 200))
            elif 'clouds' in datos_clima['description'].lower():
                draw.fill_color = Color('gray')  # Cuadrado gris
                draw.rectangle(left=100, top=100, right=200, bottom=200)
            elif 'rain' in datos_clima['description'].lower():
                draw.fill_color = Color('blue')  # Triángulo azul
                draw.polygon([(150, 150), (200, 100), (250, 150)])
            elif 'snow' in datos_clima['description'].lower():
                draw.fill_color = Color('white')  # Pentágono blanco
                draw.polygon([(150, 150), (180, 130), (210, 150), (195, 180), (165, 180)])
            else:
                draw.fill_color = Color('black')  # Texto con fondo blanco
                draw.text(50, 200, "Clima no reconocido")

            # Personalizar estilos y textos
            draw.font = '\\POO\\ProyectoFinal\\fonts\\harngton.ttf'  # Fuente para el nombre de la ciudad
            draw.font_size = 32
            draw.fill_color = Color('black')  
            draw.text(50, 250, f"Ciudad: {ciudad}")

            draw.font = '\\POO\\ProyectoFinal\\fonts\\bernhc.ttf'  # Fuente para los detalles climáticos
            draw.font_size = 28
            draw.fill_color = Color('black')  
            draw.text(50, 280, f"Temp: {datos_clima['temperatura']}°C")

            draw.fill_color = Color('black')  
            draw.text(50, 310, datos_clima['description'])

            # Crear y guardar la imagen
            with Image(width=800, height=600, background=fondo) as image:
                draw(image)
                image.save(filename=ruta_imagen)

        return ruta_imagen
    except Exception as e:
        print(f"Error al dibujar: {str(e)}")
        raise


# Ventana principal de PyQt
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.label = QtWidgets.QLabel("Consulta el clima de una ciudad", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.label)

        self.setWindowTitle("Consulta del Clima")
        self.setGeometry(100, 100, 600, 400)

        # Comenzar con el ingreso de la ciudad
        self.ingresar_ciudad()

    def ingresar_ciudad(self):
        # Ventana emergente para ingresar el nombre de la ciudad
        ciudad, ok = QtWidgets.QInputDialog.getText(self, "Ingresar Ciudad", "Nombre de la ciudad:")
        if ok and ciudad.strip():
            self.mostrar_clima(ciudad.strip())
        else:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Debes ingresar el nombre de una ciudad.")

    def mostrar_clima(self, ciudad):
        try:
            # Obtener datos del clima
            c = Clima()
            datos_clima = c.extrae_relevantes(ciudad)

            # Generar la imagen con Wand
            ruta_imagen = dibuja(ciudad, datos_clima)

            # Cargar la imagen en la interfaz
            pixmap = QtGui.QPixmap(ruta_imagen)
            self.label.setPixmap(pixmap)  # Muestra la imagen sin escalar
            self.label.setFixedSize(pixmap.size())  # Ajustar QLabel al tamaño de la imagen
            self.setWindowTitle(f"Clima en {datos_clima['ciudad']}: {datos_clima['temperatura']}°C")

            # Eliminar la imagen temporal
            os.remove(ruta_imagen)
        except requests.exceptions.RequestException as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo obtener el clima: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {str(e)}")

# Crear y ejecutar la aplicación
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
