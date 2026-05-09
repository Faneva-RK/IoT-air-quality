import smtplib, os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

MAIL_FROM     = os.getenv("MAIL_FROM")
MAIL_TO       = os.getenv("MAIL_TO")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

def send_alert_email(zone, metric, value):
    msg = MIMEText(f"""
Bonjour,

Une alarme a été détectée sur votre système IoT.

Zone     : {zone}
Métrique : {metric}
Valeur   : {value}

Action recommandée : Ventiler immédiatement la zone concernée.

-- Système IoT Air Quality Monitoring
   ENI Fianarantsoa – M2 ASR
    """)
    msg["Subject"] = f"[ALERTE IoT] {metric} élevé détecté – {zone}"
    msg["From"]    = MAIL_FROM
    msg["To"]      = MAIL_TO

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(MAIL_FROM, MAIL_PASSWORD)
            server.sendmail(MAIL_FROM, MAIL_TO, msg.as_string())
            print(f"[EMAIL] Alerte envoyée – {zone} – {metric} = {value}")
    except Exception as e:
        print(f"[EMAIL] Erreur envoi : {e}")