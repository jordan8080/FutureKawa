"""
Service d'envoi d'emails pour les alertes.

Configuration via variables d'environnement :
    SMTP_HOST       (ex: smtp.gmail.com)
    SMTP_PORT       (ex: 587)
    SMTP_USER       (ex: ton.email@gmail.com)
    SMTP_PASSWORD   (mot de passe ou app password)
    ALERT_EMAIL_TO  (destinataire = responsable d'exploitation)

Si SMTP n'est PAS configuré, les emails sont affichés dans la console
(mode démonstration) — pratique pour la soutenance sans vrai serveur mail.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO", "responsable.brazil@futurekawa.com")
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM", SMTP_USER or "alerts@futurekawa.com")

# Mode démo si SMTP non configuré
DEMO_MODE = not (SMTP_HOST and SMTP_USER and SMTP_PASSWORD)


def build_email_body(message: str, type_alerte: str, niveau: str, pays: str, lot_id: int) -> str:
    return f"""
ALERTE FUTUREKAWA — {pays.upper()}
{'=' * 45}

Niveau     : {niveau.upper()}
Type       : {type_alerte}
Lot        : #{lot_id}

{message}

{'=' * 45}
Action attendue : vérifier les conditions de l'entrepôt
et le statut du lot concerné.

Ceci est un message automatique du système de
surveillance FutureKawa.
"""


def send_alert_email(message: str, type_alerte: str, niveau: str, pays: str = "Brazil", lot_id: int = 0):
    """Envoie un email d'alerte au responsable d'exploitation du pays."""
    subject = f"[FutureKawa {pays}] Alerte {niveau} — {type_alerte}"
    body = build_email_body(message, type_alerte, niveau, pays, lot_id)

    if DEMO_MODE:
        # Mode démonstration : affichage console
        print("\n" + "=" * 50)
        print(f"[EMAIL — MODE DÉMO] À : {ALERT_EMAIL_TO}")
        print(f"Sujet : {subject}")
        print(body)
        print("=" * 50 + "\n")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = ALERT_EMAIL_FROM
        msg["To"] = ALERT_EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"[EMAIL] Alerte envoyée à {ALERT_EMAIL_TO}")
        return True

    except Exception as e:
        print(f"[EMAIL] Erreur envoi : {e}")
        return False
