import paho.mqtt.client as mqtt
import ssl, time

TOKEN = "TOKEN_ZONE1"  # remplace par ton vrai token
BROKER = "mqtt.thingsboard.cloud"
PORT = 8883

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(TOKEN)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)
client.connect(BROKER, PORT)
client.loop_start()
time.sleep(1)

# Envoyer deux pics consécutifs
client.publish("v1/devices/me/telemetry", '{"co2": 1200}')
print("[TEST] Premier pic envoyé : co2 = 1200")
time.sleep(2)

client.publish("v1/devices/me/telemetry", '{"co2": 1350}')
print("[TEST] Deuxième pic envoyé : co2 = 1350")
time.sleep(2)

client.disconnect()
print("[TEST] Terminé")