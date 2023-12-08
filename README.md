# Fase-3-Proyecto-IoT

Instrucciones para correr:

* Crear un servidor MQTT o usar uno ya creado
* Instalar python 3.9 o superior
* Instalar Pillow con el comando:
```
pip install Pillow
```
Para correr la interfaz usar desde la terminal el comando 
```
python map.py
```
Para correr el simulador de sensores usar desde la terminal el comando 
```
python sensores.py
```
Para el nodo fisico:
* Instalar Arduino IDE
* Instalar dependencia EspMQTTClient de Patrick Lapointe Vease: https://github.com/plapointe6/EspMQTTClient
* Configurar un esquematico con resistencias en Pull-Up
![imagen](https://github.com/JuanLugoS/Fase-3-Proyecto-IoT/assets/60227071/c136c9ff-fb08-4c43-ab4e-a3a68590a6d3)

Cargar en una ESP8266 en los pines D8, D7 y D6
