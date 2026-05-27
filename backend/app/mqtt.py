import json

import paho.mqtt.client as mqtt

from .database import SessionLocal

from . import models


BROKER = "localhost"

TOPIC = "futurekawa/brazil"


# ====================================
# LIMITES BRÉSIL
# ====================================

TEMP_MIN = 26
TEMP_MAX = 32

HUM_MIN = 53
HUM_MAX = 57


# ====================================
# CREATE ALERT
# ====================================

def create_alert(
    db,
    message,
    type_alerte,
    niveau,
    lot_id=1
):

    alert = models.Alert(
        message=message,
        type_alerte=type_alerte,
        niveau=niveau,
        id_lot=lot_id
    )

    db.add(alert)

    db.commit()

    print("Alerte créée :", message)


# ====================================
# CALLBACK MQTT
# ====================================

def on_message(client, userdata, msg):

    payload = json.loads(msg.payload.decode())

    print("Message reçu :", payload)

    db = SessionLocal()

    try:

        # ==========================
        # SAVE MESURE
        # ==========================

        mesure = models.Mesure(
            temperature=payload["temperature"],
            humidite=payload["humidite"],
            id_entrepot=payload["id_entrepot"]
        )

        db.add(mesure)

        db.commit()

        print("Mesure sauvegardée")


        # ==========================
        # CHECK TEMPERATURE
        # ==========================

        temperature = payload["temperature"]

        if temperature < TEMP_MIN or temperature > TEMP_MAX:

            create_alert(
                db=db,
                message=f"Température anormale : {temperature}",
                type_alerte="temperature",
                niveau="danger"
            )


        # ==========================
        # CHECK HUMIDITE
        # ==========================

        humidite = payload["humidite"]

        if humidite < HUM_MIN or humidite > HUM_MAX:

            create_alert(
                db=db,
                message=f"Humidité anormale : {humidite}",
                type_alerte="humidite",
                niveau="danger"
            )


    except Exception as e:

        print("Erreur :", e)

    finally:

        db.close()


# ====================================
# START MQTT
# ====================================

def start_mqtt():

    client = mqtt.Client()

    client.on_message = on_message

    client.connect(BROKER, 1883, 60)

    client.subscribe(TOPIC)

    print("MQTT connecté")

    client.loop_start()