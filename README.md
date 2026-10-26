# relais-sms

Un petit service web (Flask) qui **reçoit les SMS que votre téléphone Android lui transmet** et les range dans un journal `sms-log.jsonl`. Utile pour qu'un script ou un agent puisse lire un code reçu par SMS, ou garder une trace de messages précis.

## Ce que contient le dépôt
• `app.py` : le service. `POST /sms-relay` (protégé par un jeton), `GET /sms-relay/health`.
• `Dockerfile`, `docker-compose.yml`, `.env.example` : pour le lancer.
Le jeton n'est jamais dans le code : variable `SMS_RELAY_TOKEN` (le service refuse de démarrer sans un jeton d'au moins 16 caractères).

## Installer
```
git clone <ce dépôt> && cd relais-sms
cp .env.example .env
sed -i "s/^SMS_RELAY_TOKEN=.*/SMS_RELAY_TOKEN=$(openssl rand -hex 24)/" .env
docker compose up -d
curl http://127.0.0.1:8000/sms-relay/health          # {"status":"healthy"}
```
Mettez ensuite un reverse proxy HTTPS devant le port 8000 : le jeton circule dans un en-tête, ne l'exposez jamais en HTTP simple sur Internet.

## Brancher le téléphone (MacroDroid ou équivalent)
Créez une macro : **déclencheur** « SMS reçu » (filtrez sur le contact qui vous intéresse) ; **action** « Requête HTTP » :
• méthode POST, adresse `https://votre-domaine.example/sms-relay`, type `application/json` ;
• en-tête `Authorization: Bearer <votre jeton>` ;
• corps :
```
{"from_name": "[sms_name]", "from_number": "[sms_number]", "message": "[sms_message]"}
```
Aucune macro exportée n'est fournie volontairement : elle contiendrait votre jeton.

## Lire les messages
`data/sms-log.jsonl`, une ligne JSON par SMS : `ts`, `from_name`, `from_number`, `message`, `raw`. Ce fichier contient vos SMS : ne le commitez pas (il est ignoré par git).

## Sécurité
• Changez le jeton si vous le soupçonnez fuité (modifiez `.env`, `docker compose up -d`, puis la macro).
• Les SMS transitent par votre téléphone, votre réseau et votre serveur : ne relayez que ce dont vous avez besoin (filtre sur le contact).

## Licences
Code : Apache 2.0 (`LICENSE`, `NOTICE`). Texte : CC BY 4.0 (`LICENSE-docs`). Dépendances : Flask (BSD-3), Gunicorn (MIT).
