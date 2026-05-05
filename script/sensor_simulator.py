import os

import paho.mqtt.client as mqtt
import json, time, random, threading, ssl

from dotenv import load_dotenv

load_dotenv()

DEVICES = [
    {"token": os.getenv("TOKEN_ZONE1"), "zone": "zone1"},
    {"token": os.getenv("TOKEN_ZONE2"), "zone": "zone2"},
]
BROKER   = os.getenv("MQTT_BROKER", "mqtt.thingsboard.cloud")
PORT     = int(os.getenv("MQTT_PORT", 8883))
INTERVAL = int(os.getenv("MQTT_INTERVAL", 5))

def generate_data(zone):
    return {
        "co2":         round(random.gauss(600, 150), 1),
        "pm25":        round(abs(random.gauss(30, 20)), 1),
        "temperature": round(random.gauss(25, 3), 1),
        "humidity":    round(random.uniform(40, 80), 1),
        "zone":        zone
    }

def run_device(device):
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(device["token"])

    # Activation TLS
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

    client.will_set(
        "v1/devices/me/attributes",
        json.dumps({"status": "offline"}),
        retain=True
    )
    client.connect(BROKER, PORT)
    client.loop_start()
    client.publish("v1/devices/me/attributes", json.dumps({"status": "online"}))
    print(f"[TLS] {device['zone']} connecté sur port {PORT} (chiffré)")

    while True:
        data = generate_data(device["zone"])
        client.publish("v1/devices/me/telemetry", json.dumps(data))
        print(f"[SIM] {device['zone']} → {data}")
        time.sleep(INTERVAL)

for device in DEVICES:
    t = threading.Thread(target=run_device, args=(device,), daemon=True)
    t.start()

while True:
    time.sleep(1)