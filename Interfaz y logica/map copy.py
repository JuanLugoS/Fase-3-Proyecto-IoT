import tkinter as tk
from PIL import Image, ImageTk
from semaforo import Semaforo
from sensor import Sensor
from paho.mqtt import client as mqtt_client

import random
import time
from threading import *
mensaje_recibido = False
mesaje = ""
estado = ""

#Conexión MQTT
broker = '192.168.0.6'
port = 1883
topic = "semaforos"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client





def interfaz(c):
    global mensaje_recibido, mesaje, estado

    #Creacion sensores
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
        print("Clic en: ", x, y)

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

            print ("Sensor ", sensor.get_id(), " estado: ", sensor.get_estado())


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

    a = True
    while True:
        if mesaje == 'n':
            break

        c.acquire()
        c.wait()
        print ("Sync semaforo ", mesaje, mensaje_recibido)
        if mensaje_recibido:
            sincronizar_semaforos(sensores, mesaje, semaforos, canvas)
            mensaje_recibido = False
            estado = get_all_states(semaforos)
        c.release()


    root.mainloop()


    """while True:
        # Sincronizar los semáforos
        c.acquire()
        c.wait()
        print ("Sync semaforo ", mesaje, mensaje_recibido)
        if mensaje_recibido:
            sincronizar_semaforos(sensores, mesaje, semaforos, canvas)
            mensaje_recibido = False
            estado = get_all_states(semaforos)
        c.release()"""
    


def subscribe(client: mqtt_client, c):
    def on_message(client, userdata, msg):
        global mensaje_recibido, mesaje, estado
        if msg.payload.decode() != "":
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            # Recibir los estados de los sensores
        
            c.acquire()
            mensaje_recibido = True
            mesaje = msg.payload.decode()
            c.notify()
            c.release()
            time.sleep(0.1)

            c.acquire()
            result = client.publish(f"{topic}/state",estado)
            c.release()
            # result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"Send `{estado}` to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")

    client.subscribe(topic)
    client.on_message = on_message



"""while True:
    nuevo_estado = input("¿Desea actualizar los estados de los sensores? (s/n): ")

    if nuevo_estado == 'n':
        break

    # Recibir los estados de los sensores
    estados_sensores = recibir_estados()

    # Sincronizar los semáforos
    sincronizar_semaforos(sensores, estados_sensores, semaforos, canvas)

    result = client.publish(topic, get_all_states(semaforos))
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{get_all_states(semaforos)}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    print ("Semaforo ", get_all_states(semaforos))"""

def mqtt(c):
    client = connect_mqtt()
    subscribe(client, c)
    client.loop_forever()




c=Condition()
t1=Thread(target=mqtt, args=(c,))
t2=Thread(target=interfaz, args=(c,))

t1.start()
t2.start()