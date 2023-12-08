const int inputPin1 = 15;
const int inputPin2 = 13;
const int inputPin3 = 12;

int value1 = 0;
int value2 = 0;
int value3 = 0;
int value1ant = 0;
int value2ant = 0;
int value3ant = 0;
 
#include "EspMQTTClient.h"

EspMQTTClient client(
  "SSID",
  "clave",
  "192.168.0.6",  // MQTT Broker server ip
  "MQTTUsername",   // Can be omitted if not needed
  "MQTTPassword",   // Can be omitted if not needed
  "TestClient",     // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);


void setup() {
  Serial.begin(9600);
  pinMode(inputPin1, INPUT);
  pinMode(inputPin2, INPUT);
  pinMode(inputPin3, INPUT);
  client.enableDebuggingMessages(); // Enable debugging messages sent to serial output
}
 
void onConnectionEstablished()
{
  // Subscribe to "mytopic/test" and display received message to Serial
  client.subscribe("mytopic/test", [](const String & payload) {
    Serial.println(payload);
  });
}

void loop(){
  value1 = digitalRead(inputPin1);  //lectura digital de pin
  value2 = digitalRead(inputPin2);  //lectura digital de pin
  value3 = digitalRead(inputPin3);  //lectura digital de pin
 
  //mandar mensaje a puerto serie en función del valor leido
  if (value1ant != value1) {
    if (value1 == LOW) {
        client.publish("semaforos/1", "1");
        value1ant = value1;
    }
    else{
      client.publish("semaforos/1", "0");
        value1ant = value1;
    } 
  }
  
  if (value2ant != value2) {
    if (value2 == LOW) {
      client.publish("semaforos/3", "1");
      value2ant = value2;
    }
    else{
      client.publish("semaforos/3", "0");
      value2ant = value2;
    }
  }
  
  if (value3ant != value3) {
    if (value3 == LOW) {
      client.publish("semaforos/6", "1");
      value3ant = value3;
    }
    else{
      client.publish("semaforos/6", "0");
      value3ant = value3;
    }
  }
  
  client.loop();
}