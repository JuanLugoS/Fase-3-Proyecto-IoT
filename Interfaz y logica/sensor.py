
class Sensor:
    id_counter = 0  

    def __init__(self, ubicacion1,ubicacion2):
        self.ubicacion1 = ubicacion1
        self.ubicacion2 = ubicacion2
        self.ocupado = 0
        self.id_sensor = Sensor.id_counter
        Sensor.id_counter += 1  

    def set_estado(self, estado):
        self.ocupado = estado

    def get_estado(self):
        return self.ocupado

    def get_id(self):
        return self.id_sensor
exportar = Sensor

