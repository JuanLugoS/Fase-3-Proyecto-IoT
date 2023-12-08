import tkinter as tk
from PIL import Image, ImageTk
from semaforo import Semaforo
from sensor import Sensor

from paho.mqtt import client as mqtt_client
import random

from threading import *
import time

#Conexión MQTT
broker = '192.168.0.6'
port = 1883
topic = "semaforos"
client_id = f'python-mqtt-{random.randint(0, 1000)}'


sensor11 = Sensor( (547, 278), (497, 333))
sensor12 = Sensor( (418,185), (370,235))
sensor21= Sensor( (797,392), (829,351))
sensor22= Sensor( (965,438), (937,478))
sensor31= Sensor( (611, 623), (526, 619))
sensor32= Sensor( (667, 544), (579, 490))

sensores = [sensor11, sensor12, sensor21, sensor22, sensor31, sensor32]

# creacion de semaforos
semaforo1 = Semaforo(1, sensor11, sensor12, (569,309))
semaforo2 = Semaforo(2, sensor21,sensor22, (791,330))
semaforo3 = Semaforo(3, sensor31,sensor32, (611,487))
semaforos = [semaforo1, semaforo2, semaforo3]

def obtener_coordenadas(event):
    # Las coordenadas del clic se encuentran en las propiedades x y y del evento.
    x = event.x
    y = event.y
    print("   Clic en: ", x, y, "                        ", end='')

def actualizar_color_semaforos(semaforos, canvas):
    for semaforo in semaforos:
        print ("Semaforo ", semaforo.get_id(), " estado_sensor_cercano: ", semaforo.get_sensor_cercano().get_estado(), " estado_sensor_lejano: ", semaforo.get_sensor_lejano().get_estado())
        print ("Semaforo ", semaforo.get_id(), " estado_pre_funcion: ", semaforo.get_estado())
        semaforo.actualizar_estado()
        print ("Semaforo ", semaforo.get_id(), " estado_post_funcion: ", semaforo.get_estado())
        color = 'red' if semaforo.get_estado() == 'ROJO' else 'green' if semaforo.get_estado() == 'VERDE' else 'yellow'
        canvas.itemconfig(semaforo.grafico, fill=color)

def recibir_estados():
    estados_str = input("Ingresar la cadena de estados (ej. 101010): ")
    estados = list(estados_str)
    print ("Estados ingresados: ", estados)
    return estados

def actualizar_estado_sensores(sensores, estados_sensores):
    # Revisar si hay cambios en los estados de los sensores
    for i in range(len(sensores)):
        sensor = sensores[i]
        estado = estados_sensores[i]
        sensor.set_estado(estado)

        # Actualizar el color del sensor en la interfaz
        cambiar_color_sensor(sensor)


def cambiar_color_sensor(sensor):
    ##1 es ocupado, 0 es libre
    if sensor.get_estado() == '1':
        color = 'red'
    else:
        color = 'green'
    canvas.itemconfig(sensor.grafico, fill=color)

def obtener_semaforo_a_verde(semaforos):
    mejor_semaforo = None
    mejor_puntuacion = float('-inf')  # Inicializar con un valor muy bajo

    for semaforo in semaforos:
        puntuacion = 0

        # Asignar puntuaciones basadas en detección de vehículos
        if semaforo.get_sensor_cercano().get_estado() == '1' and semaforo.get_sensor_lejano().get_estado() == '1':
            puntuacion += 2
        elif semaforo.get_sensor_cercano().get_estado() == '1' or semaforo.get_sensor_lejano().get_estado() == '1':
            puntuacion += 1

        # Otorgar puntos adicionales basados en el tiempo en rojo acumulado
        #puntuacion += semaforo.tiempo_en_rojo


        if puntuacion > mejor_puntuacion or (puntuacion == mejor_puntuacion and semaforo.id_semaforo < mejor_semaforo.id_semaforo):
            mejor_puntuacion = puntuacion
            mejor_semaforo = semaforo

    return mejor_semaforo


def sincronizar_semaforos(sensores, estados_sensores, semaforos, canvas):

    # Recibir los estados de los sensores
    actualizar_estado_sensores(sensores, estados_sensores)

    # Incrementar el contador de tiempo en rojo para cada semáforo en rojo
    for semaforo in semaforos:
        if semaforo.get_estado() == 'ROJO':
            semaforo.tiempo_en_rojo += 1

    # Decidir qué semáforo debe cambiar a verde
    semaforo_a_verde = None
    max_prioridad = -1
    
    semaforo_a_verde = obtener_semaforo_a_verde(semaforos)


    # Si se encontró un semáforo para poner en verde, actualizar su estado
    if semaforo_a_verde:
        semaforo_a_verde.set_estado('VERDE')
        semaforo_a_verde.tiempo_en_rojo = 0  # Resetear el contador de tiempo en rojo

    # Poner los demás semáforos en rojo
    for semaforo in semaforos:
        if semaforo != semaforo_a_verde:
            semaforo.set_estado('ROJO')

    # Actualizar colores en la interfaz
    for semaforo in semaforos:
        color = 'red' if semaforo.get_estado() == 'ROJO' else 'green'
        canvas.itemconfig(semaforo.grafico, fill=color)

def get_all_states(semaforos):
    states = ""
    for semaforo in semaforos:
        states += semaforo.get_st_binary()
    return states

canvas = None
def interfaz(c):
    global canvas
    c.acquire()
    root = tk.Tk()
    root.title("Simulación de Semaforización")

    # Cargar la imagen de fondo
    image_path = "puntoInteres.png"
    bg_image = Image.open(image_path)
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Crear un Canvas y poner la imagen de fondo
    canvas = tk.Canvas(root, width=bg_image.width, height=bg_image.height)
    canvas.pack()
    canvas.create_image(0, 0, image=bg_photo, anchor=tk.NW)

    canvas.bind("<Button-1>", obtener_coordenadas)


    for semaforo in semaforos:
        x, y = semaforo.posicion
        # Crea un círculo que represente el semáforo, el estado inicial es rojo
        semaforo.grafico = canvas.create_oval(x-20, y-20, x+20, y+20, fill='red')

    for sensor in sensores:
        x, y = sensor.ubicacion1
        x2, y2 = sensor.ubicacion2
        # Crea una línea que represente el sensor, el estado inicial es libre con color verde
        
        sensor.grafico = canvas.create_line(x-5, y-5, x2+5, y2+5, fill='green', width=5)

    # Resetear el contador de tiempo en rojo para todos los semáforos
    for semaforo in semaforos:
        semaforo.tiempo_en_rojo = 0

    c.notify()
    c.release()
    root.mainloop()
    

se_st = ["0", "0", "0", "0", "0", "0"]

def list_to_string(s):
    str1 = ""
    for ele in s:
        str1 += ele
    return str1

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global canvas
        global se_st
        num_sem = int(msg.topic.split("/")[1]) - 1
        # Recibir los estados de los sensores
        estados_sensores = msg.payload.decode()
        se_st[num_sem] = estados_sensores
        print(f"\r{se_st}", end='')

        estados_sensores = list_to_string(se_st)
        sincronizar_semaforos(sensores, estados_sensores, semaforos, canvas)

        result = client.publish(f"estado", get_all_states(semaforos))
        status = result[0]
        if status != 0:
            print(f"Failed to send message to topic {topic}")

    client.subscribe(f"{topic}/+")
    client.on_message = on_message


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def mqtt(c):
    c.acquire()
    c.wait()
    client = connect_mqtt()
    c.release()
    subscribe(client)
    client.loop_forever()

c=Condition()
t1=Thread(target=mqtt, args=(c,))
t2=Thread(target=interfaz, args=(c,))

t1.start()
t2.start()