import random
import json
import time

import paho.mqtt.publish as publish


TOPIC = "futurekawa/brazil"

BROKER = "localhost"


while True:

    data = {
    "temperature":30,
    "humidite":55,
    "id_entrepot": 1
    }

    publish.single(
        TOPIC,
        json.dumps(data),
        hostname=BROKER
    )

    print("Data sent :", data)

    time.sleep(5)