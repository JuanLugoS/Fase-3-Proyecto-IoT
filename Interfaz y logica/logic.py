def main():
    # Crear sensores y semáforos aquí, asumiendo que ya se han creado
    sensores = [...]  
    semaforos = [...]  

    while True:
        # Imprimir el estado actual de todos los semáforos
        for semaforo in semaforos:
            print(f"Semaforo {semaforo.id_semaforo}: {semaforo.get_estado()}")

        # Pedir al usuario que cambie el estado de un sensor
        sensor_id = int(input("Ingrese el ID del sensor a cambiar (0 para salir): "))
        if sensor_id == 0:
            break
        nuevo_estado = int(input("Ingrese el nuevo estado para el sensor (0 o 1): "))
        
        # Cambiar el estado del sensor y actualizar el semáforo correspondiente
        sensores[sensor_id].set_estado(nuevo_estado)
        for semaforo in semaforos:
            semaforo.actualizar_estado()

if __name__ == "__main__":
    main()
