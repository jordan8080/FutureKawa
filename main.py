import network # type: ignore
import time
from machine import Pin # type: ignore
import dht # type: ignore
import ujson # type: ignore
from umqtt.simple import MQTTClient  # type: ignore

"""

BASED ON MicroPython ESP32 DHT22 MQTT
by artefatos
https://wokwi.com/projects/395442253921303553



USE WOKWI HOBBY + 


"""


# MQTT Server Parameters
MQTT_CLIENT_ID = " "
MQTT_BROKER    = "host.wokwi.internal" 
MQTT_PORT = 1883
MQTT_USER      = " "
MQTT_PASSWORD  = " "
MQTT_TOPIC     = " "

sensor = dht.DHT22(Pin(15))

print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
client.connect()

print("Connected!")


while True:
  print("Measuring weather conditions... ", end="")
  try:
    sensor.measure() 
    message = ujson.dumps({
      "temp": sensor.temperature(),
      "humidity": sensor.humidity(),
    })
  except Exception as e:
    print("Erreur :", e)
    
  time.sleep(30)
  print("Updated!")
  print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
  client.publish(MQTT_TOPIC, message)
    
  
 


