import json
import os

import paho.mqtt.client as mqtt

from .database import SessionLocal
from . import models
from .alerts import check_and_create_alerts_from_mesure

BROKER = os.getenv("MQTT_BROKER", "localhost")
TOPIC = os.getenv("MQTT_TOPIC", "futurekawa/brazil")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[MQTT] Connecté au broker {BROKER}")
        client.subscribe(TOPIC)
        print(f"[MQTT] Abonné au topic : {TOPIC}")
    else:
        print(f"[MQTT] Erreur connexion : code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"[MQTT] Message reçu : {payload}")

        db = SessionLocal()

        try:
            # Sauvegarde mesure
            mesure = models.Mesure(
                temperature=payload.get("temperature"),
                humidite=payload.get("humidite"),
                Id_entrepot=payload.get("Id_entrepot", 1)
            )
            db.add(mesure)
            db.commit()
            print("[MQTT] Mesure sauvegardée")

            # Vérification alertes automatiques (par entrepôt)
            entrepot_id = payload.get("Id_entrepot", 1)
            check_and_create_alerts_from_mesure(
                db=db,
                temperature=float(payload.get("temperature", 0)),
                humidite=float(payload.get("humidite", 0)),
                entrepot_id=entrepot_id
            )

        except Exception as e:
            db.rollback()
            print(f"[MQTT] Erreur sauvegarde : {e}")

        finally:
            db.close()

    except json.JSONDecodeError as e:
        print(f"[MQTT] Erreur décodage JSON : {e}")


def start_mqtt():
    try:
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, 1883, 60)
        client.loop_start()
        print(f"[MQTT] Service démarré (broker: {BROKER}, topic: {TOPIC})")
    except Exception as e:
        print(f"[MQTT] Impossible de se connecter au broker : {e}")
        print("[MQTT] Backend continue sans MQTT")
