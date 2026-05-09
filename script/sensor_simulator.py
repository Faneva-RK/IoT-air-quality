import paho.mqtt.client as mqtt
import json, time, random, threading, ssl, os, signal, sys
from dotenv import load_dotenv
from envoi_email import send_alert_email

load_dotenv()

DEVICES = [
    {"token": os.getenv("TOKEN_ZONE1"), "zone": "zone1"},
    {"token": os.getenv("TOKEN_ZONE2"), "zone": "zone2"},
]
BROKER   = os.getenv("MQTT_BROKER", "mqtt.thingsboard.cloud")
PORT     = int(os.getenv("MQTT_PORT", 8883))
INTERVAL = int(os.getenv("MQTT_INTERVAL", 5))

# Liste globale des clients actifs pour le shutdown propre
active_clients = []

def generate_data(zone):
    return {
        "co2":         round(random.gauss(600, 150), 1),
        "pm25":        round(abs(random.gauss(30, 20)), 1),
        "temperature": round(random.gauss(25, 3), 1),
        "humidity":    round(random.uniform(40, 80), 1),
        "zone":        zone
    }
""" def generate_data(zone):
    return {
    "co2":         1500.0,   # forcé au dessus de 1000
    "pm25":        round(abs(random.gauss(30, 20)), 1),
    "temperature": round(random.gauss(25, 3), 1),
    "humidity":    round(random.uniform(40, 80), 1),
    "zone":        zone
} """

def run_device(device):
    interval = INTERVAL

    # Eviter les emails répétés tant que la valeur reste élevée
    email_sent = {
        "co2_warning":   False,
        "co2_critical":  False,
        "pm25_warning":  False,
        "pm25_critical": False
    }

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"[TLS] {device['zone']} connecté sur {BROKER}:{PORT}")
        client.subscribe("v1/devices/me/rpc/request/+")
        client.publish(
            "v1/devices/me/attributes",
            json.dumps({"status": "online"})
        )

    def on_disconnect(client, userdata, flags, reason_code, properties):
        print(f"[SIM] {device['zone']} déconnecté (code: {reason_code})")

    def on_message(client, userdata, msg):
        nonlocal interval
        try:
            data = json.loads(msg.payload)
            method = data.get("method", "")
            params = data.get("params", None)

            if method == "setInterval" and params is not None:
                interval = int(params)
                print(f"[RPC] {device['zone']} → intervalle changé à {interval}s")
                request_id = msg.topic.split("/")[-1]
                client.publish(
                    f"v1/devices/me/rpc/response/{request_id}",
                    json.dumps({"status": "ok", "interval": interval})
                )
        except Exception as e:
            print(f"[RPC] Erreur : {e}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(device["token"])
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

    # LWT – publié automatiquement si connexion coupée brutalement
    client.will_set(
        "v1/devices/me/attributes",
        json.dumps({"status": "offline"}),
        retain=True
    )

    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect
    client.on_message    = on_message

    client.connect(BROKER, PORT)
    client.loop_start()

    # Ajouter ce client à la liste globale pour le shutdown
    active_clients.append(client)

    while True:
        data = generate_data(device["zone"])
        client.publish("v1/devices/me/telemetry", json.dumps(data))
        print(f"[SIM] {device['zone']} → {data}")

        # Vérification CO2 Critical
        if data["co2"] > 2000 and not email_sent["co2_critical"]:
            send_alert_email(device["zone"], "CO2 CRITIQUE", f"{data['co2']} ppm")
            email_sent["co2_critical"] = True
        elif data["co2"] <= 2000:
            email_sent["co2_critical"] = False

        # Vérification CO2 Warning
        if data["co2"] > 1000 and not email_sent["co2_warning"]:
            send_alert_email(device["zone"], "CO2 élevé", f"{data['co2']} ppm")
            email_sent["co2_warning"] = True
        elif data["co2"] <= 1000:
            email_sent["co2_warning"] = False

        # Vérification PM2.5 Critical
        if data["pm25"] > 75 and not email_sent["pm25_critical"]:
            send_alert_email(device["zone"], "PM2.5 CRITIQUE", f"{data['pm25']} µg/m³")
            email_sent["pm25_critical"] = True
        elif data["pm25"] <= 75:
            email_sent["pm25_critical"] = False

        # Vérification PM2.5 Warning
        if data["pm25"] > 35 and not email_sent["pm25_warning"]:
            send_alert_email(device["zone"], "PM2.5 élevé", f"{data['pm25']} µg/m³")
            email_sent["pm25_warning"] = True
        elif data["pm25"] <= 35:
            email_sent["pm25_warning"] = False

        time.sleep(interval)


def shutdown(sig, frame):
    print("\n[SIM] Arrêt en cours – publication statut offline...")
    for client in active_clients:
        try:
            client.publish(
                "v1/devices/me/attributes",
                json.dumps({"status": "offline"})
            )
            time.sleep(0.5)
            client.disconnect()
        except Exception as e:
            print(f"[SIM] Erreur lors de l'arrêt : {e}")
    print("[SIM] Tous les devices sont offline. Arrêt terminé.")
    sys.exit(0)

# Intercepter Ctrl+C pour un arrêt propre
signal.signal(signal.SIGINT, shutdown)

# Lancer les deux zones en parallèle
for device in DEVICES:
    t = threading.Thread(target=run_device, args=(device,), daemon=True)
    t.start()

print("[SIM] Simulateur démarré – Ctrl+C pour arrêter proprement")

# Garder le script principal en vie
while True:
    time.sleep(1)