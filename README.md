🌫️ IoT Air Quality Monitoring
Projet M2 Administration Systèmes et Réseaux – ENI Fianarantsoa
Surveillance de la qualité de l'air en temps réel via MQTT et Thingsboard Cloud.

📋 Description
Ce projet simule un système IoT de surveillance de la qualité de l'air sur deux zones géographiques distinctes. Un script Python génère des données de capteurs environnementaux et les envoie en temps réel vers la plateforme Thingsboard Cloud via le protocole MQTT sécurisé (TLS). Les données sont visualisées sur un dashboard interactif avec des alertes automatiques en cas de dépassement de seuils sanitaires.
Problématique résolue : La qualité de l'air dans un espace fermé se dégrade progressivement sans que les occupants s'en rendent compte. Un taux de CO₂ élevé provoque fatigue et baisse de concentration. Les particules fines PM2.5 ont des effets respiratoires à long terme. Sans surveillance, personne ne sait quand la situation devient dangereuse.

🏗️ Architecture
[Script Python]
      |
      |  MQTT over TLS (port 8883)
      v
[Thingsboard Cloud]
      |
      |-- Stockage time-series
      |-- Règles d'alarme automatiques
      |-- Détection online/offline (LWT)
      v
[Dashboard Thingsboard]
      |
      |-- Time series charts (CO₂, PM2.5)
      |-- Gauges (Température, Humidité)
      |-- Alarms table
      |-- Statut device

📊 Données simulées
Les données sont générées avec random.gauss() pour produire des variations réalistes simulant de vrais capteurs.

🗂️ Structure du projet
iot-air-quality/
├── simulator/
│   ├── sensor_simulator.py   # Script principal
│   └── requirements.txt      # Dépendances Python
├── .env                      # Tokens et config (non committé)
├── .env.example              # Exemple de config sans secrets
├── .gitignore
└── README.md

⚙️ Prérequis

Python 3.11+
pip
Un compte gratuit sur thingsboard.cloud
mosquitto-clients pour les tests en ligne de commande (optionnel)
Wireshark pour les tests de sécurité (optionnel)


🚀 Installation et lancement
1. Cloner le projet
bashgit clone https://github.com/ton-user/iot-air-quality.git
cd iot-air-quality
2. Installer les dépendances Python
bashpip install -r simulator/requirements.txt
3. Configurer les variables d'environnement
bashcp .env.example .env

Édite .env et remplis tes tokens Thingsboard :
envTOKEN_ZONE1=TON_TOKEN_ZONE1
TOKEN_ZONE2=TON_TOKEN_ZONE2
MQTT_BROKER=mqtt.thingsboard.cloud
MQTT_PORT=8883
MQTT_INTERVAL=5
4. Lancer le simulateur
bashpython simulator/sensor_simulator.py
Tu dois voir dans le terminal :
[TLS] zone1 connecté sur mqtt.thingsboard.cloud:8883
[TLS] zone2 connecté sur mqtt.thingsboard.cloud:8883
[SIM] zone1 → {'co2': 643.2, 'pm25': 18.4, 'temperature': 24.7, 'humidity': 58.3, 'zone': 'zone1'}
[SIM] zone2 → {'co2': 571.8, 'pm25': 22.1, 'temperature': 23.9, 'humidity': 61.2, 'zone': 'zone2'}

🔧 Configuration Thingsboard
Devices
DeviceZoneProfileair-quality-sensor-zone1Salle B204air-quality-profileair-quality-sensor-zone2Salle B205air-quality-profile
Device Profile
Un seul profile air-quality-profile est partagé par les deux devices. Il contient toutes les règles d'alarme. Toute modification du profile s'applique automatiquement aux deux zones.
Attributs statiques par device
json{
  "location": "Salle B204",
  "sensor_model": "Simulated MQ-135 + DHT22",
  "firmware_version": "1.0.0"
}

🔔 Règles d'alarme
AlarmeConditionSévéritéRésolution automatiqueCO₂ élevéco2 > 1000 ppmWarningco2 ≤ 1000CO₂ critiqueco2 > 2000 ppmCriticalco2 ≤ 2000PM2.5 élevépm25 > 35 µg/m³Warningpm25 ≤ 35PM2.5 critiquepm25 > 75 µg/m³Criticalpm25 ≤ 75

📺 Dashboards
Deux dashboards identiques, un par zone, chacun contenant :

Time series chart CO₂ : courbe temporelle en ppm
Time series chart PM2.5 : courbe temporelle en µg/m³
Gauge Température : jauge colorée en °C
Gauge Humidité : jauge colorée en %
Alarms table : historique des alarmes avec horodatage
Statut device : online / offline en temps réel
Sélecteur de période : 5 min, 1h, 24h


🔒 Sécurité
Mécanismes implémentés
MécanismeDescriptionToken par deviceChaque device a un token unique. Sans token valide, la connexion MQTT est refuséeMQTT over TLSConnexion sur port 8883, données chiffrées avec TLSv1.3Last Will and TestamentThingsboard détecte automatiquement la déconnexion et passe le device en offlineHTTPS dashboardInterface web accessible uniquement en HTTPS
Vérifier le certificat TLS
bashopenssl s_client -connect mqtt.thingsboard.cloud:8883
Tester le refus sans token
bashmosquitto_pub -h mqtt.thingsboard.cloud -p 8883 \
  -u "mauvais_token" \
  -t v1/devices/me/telemetry \
  -m '{"co2": 500}'
Résultat attendu : connexion refusée.

🧪 Plan de tests
Tests fonctionnels
IDTestRésultat attenduT01Lancer le scriptLes deux zones affichent connecté dans le terminalT02Latest telemetry zone1Les 4 métriques se mettent à jour toutes les 5sT03Latest telemetry zone2IdemT04Dashboard zone14 widgets actifs avec données en temps réelT05Dashboard zone2IdemT06Alarme CO₂ WarningForcer co2 > 1000 → alarme visible dans Alarms tableT07Alarme CO₂ CriticalForcer co2 > 2000 → alarme Critical déclenchéeT08Résolution automatiqueValeur redescend → alarme résolue automatiquementT09Statut offlineCouper le script → devices passent offline
