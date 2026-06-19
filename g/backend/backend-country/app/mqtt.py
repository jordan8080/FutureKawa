"""Abonné MQTT : reçoit les mesures des capteurs et déclenche le stockage + alertes.

Topic : futurekawa/<pays>/<warehouseId>/measurement
Payload JSON : {"warehouseId": "...", "temperature": 28.4, "humidity": 54.1}
"""
import json
import threading

import paho.mqtt.client as mqtt

from . import alerts, config, crud
from .database import SessionLocal


def _on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"[MQTT] Connecté ({reason_code}) — abonnement à {config.MQTT_TOPIC}", flush=True)
    client.subscribe(config.MQTT_TOPIC)


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        warehouse_id = payload["warehouseId"]
        temperature = float(payload["temperature"])
        humidity = float(payload["humidity"])
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"[MQTT] Payload invalide sur {msg.topic}: {exc}", flush=True)
        return

    db = SessionLocal()
    try:
        warehouse = crud.get_warehouse(db, warehouse_id)
        if warehouse is None:
            return  # entrepôt inconnu pour ce pays
        crud.add_measurement(db, warehouse_id, temperature, humidity)
        alerts.evaluate_measurement(db, warehouse, temperature, humidity)
    except Exception as exc:  # noqa: BLE001
        print(f"[MQTT] Erreur de traitement: {exc}", flush=True)
        db.rollback()
    finally:
        db.close()


def _run():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message
    while True:
        try:
            client.connect(config.MQTT_HOST, config.MQTT_PORT, keepalive=60)
            client.loop_forever()
        except Exception as exc:  # noqa: BLE001
            print(f"[MQTT] Connexion impossible ({exc}), nouvel essai dans 5s", flush=True)
            import time
            time.sleep(5)


def start_mqtt():
    thread = threading.Thread(target=_run, daemon=True, name="mqtt-subscriber")
    thread.start()
    return thread
