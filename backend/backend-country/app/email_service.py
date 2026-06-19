"""Envoi d'email au responsable pays. Mode démo console si SMTP non configuré."""
import smtplib
from email.mime.text import MIMEText

from . import config


def send_alert_email(subject: str, body: str):
    to_addr = config.CONFIG["manager_email"]

    if not config.SMTP_HOST:
        # Mode démo : on affiche l'email dans la console.
        print("\n" + "=" * 60)
        print("[EMAIL DÉMO] (SMTP non configuré)")
        print(f"  À      : {config.CONFIG['manager']} <{to_addr}>")
        print(f"  Objet  : {subject}")
        print(f"  Corps  : {body}")
        print("=" * 60 + "\n", flush=True)
        return

    try:
        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = config.SMTP_FROM
        msg["To"] = to_addr

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as server:
            if config.SMTP_USE_TLS:
                server.starttls()
            if config.SMTP_USER:
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_FROM, [to_addr], msg.as_string())
        print(f"[EMAIL] Envoyé à {to_addr} : {subject}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"[EMAIL] Échec d'envoi ({exc}). Objet: {subject}", flush=True)
