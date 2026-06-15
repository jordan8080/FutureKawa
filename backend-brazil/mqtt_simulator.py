"""
Simulateur IoT - simule un ESP32 + DHT22 envoyant des données MQTT
Lance ce script dans un terminal séparé pendant que le backend tourne.

Usage:
    python mqtt_simulator.py

    # Avec des valeurs anormales (génère des alertes) :
    python mqtt_simulator.py --anomalies
"""

import random
import json
import time
import argparse
import sys

try:
    import paho.mqtt.publish as publish
except ImportError:
    print("Installez paho-mqtt : pip install paho-mqtt")
    sys.exit(1)

BROKER = "localhost"
TOPIC = "futurekawa/brazil"
INTERVAL = 5  # secondes entre chaque envoi

# Seuils normaux Brésil
TEMP_MIN = 26
TEMP_MAX = 32
HUM_MIN = 53
HUM_MAX = 57


def generate_normal():
    """Données dans les seuils acceptables"""
    return {
        "temperature": round(random.uniform(TEMP_MIN, TEMP_MAX), 2),
        "humidite": round(random.uniform(HUM_MIN, HUM_MAX), 2),
        "Id_entrepot": 1,
        "lot_id": 1
    }


def generate_with_anomalies():
    """Données qui dépassent parfois les seuils (génère des alertes)"""
    # 30% de chance d'anomalie température
    temp = round(random.uniform(22, 38), 2)
    # 30% de chance d'anomalie humidité
    hum = round(random.uniform(45, 68), 2)
    return {
        "temperature": temp,
        "humidite": hum,
        "Id_entrepot": 1,
        "lot_id": 1
    }


def main():
    parser = argparse.ArgumentParser(description="Simulateur MQTT FutureKawa")
    parser.add_argument("--anomalies", action="store_true", help="Générer des données anormales")
    parser.add_argument("--interval", type=int, default=INTERVAL, help="Intervalle en secondes")
    args = parser.parse_args()

    mode = "ANOMALIES" if args.anomalies else "NORMAL"
    print(f"[SIM] Simulateur démarré — mode: {mode}")
    print(f"[SIM] Broker: {BROKER} | Topic: {TOPIC} | Interval: {args.interval}s")
    print("[SIM] Appuyez Ctrl+C pour arrêter\n")

    count = 0
    while True:
        try:
            if args.anomalies:
                data = generate_with_anomalies()
            else:
                data = generate_normal()

            publish.single(
                TOPIC,
                json.dumps(data),
                hostname=BROKER,
                port=1883
            )

            count += 1
            temp_status = "⚠️ HORS SEUIL" if data["temperature"] < TEMP_MIN or data["temperature"] > TEMP_MAX else "✅ OK"
            hum_status = "⚠️ HORS SEUIL" if data["humidite"] < HUM_MIN or data["humidite"] > HUM_MAX else "✅ OK"

            print(f"[{count}] Envoyé → Temp: {data['temperature']}°C {temp_status} | Hum: {data['humidite']}% {hum_status}")

            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n[SIM] Simulateur arrêté")
            break
        except Exception as e:
            print(f"[SIM] Erreur : {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()
