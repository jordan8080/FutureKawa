# Dispositif d'alerte — FutureKawa Brésil

Document exigé par le cahier des charges (III.4 : *« Le dispositif d'alerte doit être
documenté : règles, seuils, fréquence de vérification, contenu des emails »*).

## 1. Règles de déclenchement

Le système lève une alerte automatique dans les cas suivants :

| Cas | Condition | Type | Niveau |
|-----|-----------|------|--------|
| Conditions non idéales — température | température hors plage du pays | `temperature` | `warning` (ou `critical` si écart > 3°C au-delà du seuil) |
| Conditions non idéales — humidité | humidité hors plage du pays | `humidite` | `warning` (ou `critical` si écart > 5%) |
| Lot trop ancien | > 365 jours depuis `date_stockage` | `lot_ancien` | `warning` |
| Lot expiré | `date_expiration` dépassée | `expiration` | `critical` |
| Pré-expiration (complément) | expiration dans ≤ 30 jours | `expiration_proche` | `warning` |

> Les cas « Conditions non idéales » et « Lot trop ancien » correspondent exactement
> aux deux cas exigés par le cahier des charges. Les règles d'expiration/pré-expiration
> sont des compléments métier (gestion fine de la péremption).

## 2. Seuils par pays

Les seuils sont stockés en base (table `pays`) et donc **modifiables sans redéploiement**.
Ils sont dérivés des conditions idéales ± tolérance du sujet (±3°C, ±2% humidité) :

| Pays | Température idéale | Plage acceptable | Humidité idéale | Plage acceptable |
|------|-------------------|------------------|-----------------|------------------|
| Brésil | 29°C | 26 – 32°C | 55% | 53 – 57% |
| Équateur | 31°C | 28 – 34°C | 60% | 58 – 62% |
| Colombie | 26°C | 23 – 29°C | 80% | 78 – 82% |

(Seul le Brésil est instancié dans ce prototype ; les autres sont prêts à être ajoutés.)

## 3. Fréquence de vérification

- **Conditions (temp/humidité)** : vérifiées **à chaque mesure reçue** (MQTT ou API).
  Avec le simulateur réglé à 5 s, la vérification est quasi temps réel.
- **Âge / expiration des lots** : déclenchée par l'appel `POST /lots/check-expiration`.
  En production on la planifierait quotidiennement (cron / APScheduler).

## 4. Anti-duplication

Une alerte identique (même message + même lot) n'est **jamais recréée** : pas de spam
en base ni d'email répété. L'email n'est envoyé qu'à la **création** d'une nouvelle alerte.

## 5. Contenu de l'email

Destinataire : responsable d'exploitation du pays (`ALERT_EMAIL_TO`).

```
Sujet : [FutureKawa Brazil] Alerte critical — temperature

ALERTE FUTUREKAWA — BRAZIL
=============================================
Niveau     : CRITICAL
Type       : temperature
Lot        : #3

Température anormale entrepôt #1 : 35.0°C (seuil Brazil : 26-32°C)
=============================================
Action attendue : vérifier les conditions de l'entrepôt
et le statut du lot concerné.
```

## 6. Configuration email (SMTP)

Variables d'environnement (voir `.env.example`) :

| Variable | Rôle |
|----------|------|
| `SMTP_HOST` / `SMTP_PORT` | serveur SMTP |
| `SMTP_USER` / `SMTP_PASSWORD` | authentification |
| `ALERT_EMAIL_TO` | destinataire (responsable) |

**Mode démonstration** : si SMTP n'est pas configuré, les emails sont affichés dans la
console du backend. Idéal pour la soutenance sans serveur mail (ou utiliser
[Mailtrap](https://mailtrap.io) / un mot de passe d'application Gmail pour un vrai envoi).
