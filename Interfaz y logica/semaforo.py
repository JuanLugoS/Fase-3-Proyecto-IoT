class Semaforo:
    def __init__(self, id_semaforo, sensor_cercano, sensor_lejano, posicion):
        self.id_semaforo = id_semaforo
        self.sensor_cercano = sensor_cercano
        self.sensor_lejano = sensor_lejano
        self.estado = 'ROJO'
        self.posicion = posicion
        self.tiempo_en_rojo = 0

    def actualizar_estado(self):
        # Lógica para cambiar el estado del semáforo basado en los sensores
        if self.sensor_cercano.get_estado() == '1' or self.sensor_lejano.get_estado() == '1':
            self.transicionYellow()  # Cambiar a amarillo antes de verde
            # Aquí podría haber una pausa o alguna lógica adicional
            self.estado = 'VERDE'
        else:
            self.transicionYellow()  # Cambiar a amarillo antes de rojo
            # Aquí podría haber una pausa o alguna lógica adicional
            self.estado = 'ROJO'

    def transicionYellow(self):
        self.estado = 'AMARILLO'
        # Aquí podría haber una pausa o alguna lógica adicional

    def get_id(self):
        return self.id_semaforo

    def get_sensor_cercano(self):
        return self.sensor_cercano

    def get_sensor_lejano(self):
        return self.sensor_lejano

    def get_estado(self):
        return self.estado

    def set_estado(self, estado):
        self.estado = estado

    def get_st_binary(self):
        if self.estado == 'VERDE':
            return '1'
        else:
            return '0'

