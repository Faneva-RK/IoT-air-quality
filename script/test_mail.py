from envoi_email import send_alert_email

print("[TEST] Envoi email de test...")
send_alert_email("zone1", "CO2", 1500)
print("[TEST] Terminé – vérifie ta boîte mail")