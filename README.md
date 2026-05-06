# IoT Air Quality Monitoring

Projet M2 Administration Systèmes et Réseaux - ENI Fianarantsoa.

Ce projet simule la surveillance en temps réel de la qualité de l'air sur deux zones, avec envoi de télémétrie MQTT vers ThingsBoard Cloud en TLS.

## Vue d'ensemble

Le script Python génère des mesures environnementales réalistes pour deux capteurs virtuels:

- `zone1`
- `zone2`

Chaque device publie:

- `co2`
- `pm25`
- `temperature`
- `humidity`
- `zone`

Les données sont envoyées vers ThingsBoard Cloud via MQTT sécurisé sur le port `8883`.

## Architecture

```text
sensor_simulator.py
    |
    |  MQTT over TLS
    v
ThingsBoard Cloud
    |
    |-- Stockage des télémétries
    |-- Règles d'alarmes
    |-- Détection online/offline via LWT
    v
Dashboard ThingsBoard
```

## Arborescence

```text
IoT/
├── README.md
├── capture/
│   ├── Apres-TLS.png
│   ├── Avant-TLS.png
│   ├── Connexion-tls-reussit.png
│   ├── DAshboard.png
│   ├── latest-telemetry-apres-lancement script.png
│   ├── script envoi des données.png
│   └── token.png
└── script/
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── requirements.txt
    └── sensor_simulator.py
```

## Prérequis

- Python 3.11 ou plus récent
- `pip`
- Un compte ThingsBoard Cloud

## Installation

Depuis la racine du projet:

```powershell
cd script
pip install -r requirements.txt
```

## Configuration

Le projet utilise un fichier `.env` local dans le dossier `script/`.

Copie le modèle fourni et renseigne tes propres tokens:

```powershell
copy .env.example .env
```

Variables attendues:

- `TOKEN_ZONE1`
- `TOKEN_ZONE2`
- `MQTT_BROKER`
- `MQTT_PORT`
- `MQTT_INTERVAL`

## Lancement

Depuis le dossier `script/`:

```powershell
python sensor_simulator.py
```

Le terminal doit afficher:

```text
[TLS] zone1 connecte sur port 8883 (chiffre)
[TLS] zone2 connecte sur port 8883 (chiffre)
[SIM] zone1 -> {...}
[SIM] zone2 -> {...}
```

## Fonctionnement

Le script:

- ouvre deux clients MQTT, un par zone
- s'authentifie avec un token ThingsBoard par device
- active TLS
- publie un statut `online` à la connexion
- envoie régulièrement la télémétrie
- définit un Last Will and Testament pour marquer le device `offline` en cas de coupure

## Données simulées

Les valeurs sont générées aléatoirement pour rester crédibles:

- `co2` autour de 600 ppm
- `pm25` avec variabilité autour de 30
- `temperature` autour de 25 °C
- `humidity` entre 40 % et 80 %

## Captures

Les captures sont disponibles dans `capture/`:

- `Avant-TLS.png`
- `Apres-TLS.png`
- `Connexion-tls-reussit.png`
- `DAshboard.png`
- `latest-telemetry-apres-lancement script.png`
- `script envoi des données.png`
- `token.png`


