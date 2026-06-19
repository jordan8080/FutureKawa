"""Simulateur de capteurs ESP32 + DHT22.

Publie température/humidité en MQTT pour les entrepôts des 3 pays.
Topic   : futurekawa/<pays>/<warehouseId>/measurement
Payload : {"warehouseId": "...", "temperature": 28.4, "humidity": 54.1}

Variables d'environnement :
  MQTT_HOST, MQTT_PORT
  SIM_MODE      = normal | anomalies   (anomalies = valeurs hors seuil → alertes)
  SIM_INTERVAL  = secondes entre deux cycles (défaut 10)
"""
import json
import os
import random
import time

import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
SIM_MODE = os.getenv("SIM_MODE", "normal").lower()
SIM_INTERVAL = float(os.getenv("SIM_INTERVAL", "10"))
ANOMALY_RATE = float(os.getenv("SIM_ANOMALY_RATE", "0.35"))

# (pays, warehouseId, ideal_temp, ideal_humidity)
WAREHOUSES = [
    ("brazil", "w-br-1", 29, 55),
    ("brazil", "w-br-2", 29, 55),
    ("ecuador", "w-ec-1", 31, 60),
    ("ecuador", "w-ec-2", 31, 60),
    ("colombia", "w-co-1", 26, 80),
    ("colombia", "w-co-2", 26, 80),
]

TOL_TEMP = 3
TOL_HUM = 2


def _reading(ideal_temp, ideal_hum, anomaly: bool):
    if anomaly:
        # Pousse au-delà de la tolérance pour déclencher une alerte.
        temp = ideal_temp + random.choice([-1, 1]) * random.uniform(TOL_TEMP + 1, TOL_TEMP + 4)
        hum = ideal_hum + random.choice([-1, 1]) * random.uniform(TOL_HUM + 1, TOL_HUM + 3)
    else:
        temp = ideal_temp + random.uniform(-(TOL_TEMP - 1), TOL_TEMP - 1)
        hum = ideal_hum + random.uniform(-(TOL_HUM - 0.5), TOL_HUM - 0.5)
    return round(temp, 1), round(max(0, min(100, hum)), 1)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    while True:
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            break
        except Exception as exc:  # noqa: BLE001
            print(f"[SIM] Broker indisponible ({exc}), nouvel essai dans 5s", flush=True)
            time.sleep(5)
    client.loop_start()
    print(f"[SIM] Démarré — mode={SIM_MODE}, intervalle={SIM_INTERVAL}s", flush=True)

    while True:
        for country, wid, it, ih in WAREHOUSES:
            anomaly = SIM_MODE == "anomalies" and random.random() < ANOMALY_RATE
            temp, hum = _reading(it, ih, anomaly)
            payload = json.dumps({"warehouseId": wid, "temperature": temp, "humidity": hum})
            topic = f"futurekawa/{country}/{wid}/measurement"
            client.publish(topic, payload)
            flag = " ⚠ ANOMALIE" if anomaly else ""
            print(f"[SIM] {topic} -> {temp}°C / {hum}%{flag}", flush=True)
        time.sleep(SIM_INTERVAL)


if __name__ == "__main__":
    main()
