from paho.mqtt import client as mqtt_client
import random
import time
from threading import *

#Conexión MQTT
broker = '192.168.0.6'
port = 1883
topic = "estado"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

semaforo1 = []
semaforo2 = []
semaforo3 = []

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


semaforo_en_verde = 1
client = None

def avanzar_semaforo(semaforo, en_verde, num_sem):
    if 1 in semaforo:
        if en_verde == num_sem:
            if len(semaforo) > 0 and semaforo[0] == 1:
                semaforo[0] = 0
            else:
                semaforo = semaforo[1:] 
        else:
            if len(semaforo) > 0 and semaforo[0] == 0:
                semaforo = semaforo[1:] 
    return semaforo

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global semaforo1, semaforo2, semaforo3, semaforo_en_verde
        event.clear()
        estados_sensores = list(msg.payload.decode())
        if estados_sensores[0] == '1':
            semaforo_en_verde = 1
        elif estados_sensores[1] == '1':
            semaforo_en_verde = 2
        elif estados_sensores[2] == '1':
            semaforo_en_verde = 3
        #print(f"{estados_sensores}")
        event.set()
        

    client.subscribe("estado")
    client.on_message = on_message

def mqtt():
    global client
    client = connect_mqtt()
    event.set()
    subscribe(client)
    client.loop_forever()

def publicar_estados(client: mqtt_client, n1, n2, semaforo):
    if len(semaforo) > 1:
        client.publish(f"semaforos/{n1}", semaforo[0])
        client.publish(f"semaforos/{n2}", semaforo[1])
    elif len(semaforo) > 0:
        client.publish(f"semaforos/{n1}", semaforo[0])
        client.publish(f"semaforos/{n2}", "0")
    else:
        client.publish(f"semaforos/{n1}", "0")
        client.publish(f"semaforos/{n2}", "0")

def add_trafic():
    global semaforo1, semaforo2, semaforo3, semaforo_en_verde
    global client
    event.wait()
    while event.is_set():
        print(semaforo1, semaforo2, semaforo3, semaforo_en_verde, "                                                   ", end='\r')
        sale = random.randint(0,3)
        if sale == 1:
            if semaforo1 == []:
                semaforo1.append(0)
            semaforo1.append(1)
        elif sale == 2:
            if semaforo2 == []:
                semaforo2.append(0)
            semaforo2.append(1)
        elif sale == 3:
            if semaforo3 == []:
                semaforo3.append(0)
            semaforo3.append(1)
        semaforo1 = avanzar_semaforo(semaforo1, semaforo_en_verde, 1)
        semaforo2 = avanzar_semaforo(semaforo2, semaforo_en_verde, 2)
        semaforo3 = avanzar_semaforo(semaforo3, semaforo_en_verde, 3)

        publicar_estados(client, 1, 2, semaforo1)
        publicar_estados(client, 3, 4, semaforo2)
        publicar_estados(client, 6, 5, semaforo3)

        time.sleep(2)

event=Event() 
t1=Thread(target=mqtt)
t2=Thread(target=add_trafic)

t1.start()
t2.start()

