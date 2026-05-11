import os
import requests
from flask import Flask, request, jsonify
import anthropicapp = Flask(__name__)

ULTRAMSG_TOKEN = os.environ.get("ULTRAMSG_TOKEN", "h678qqkz2cws7dt5")
ULTRAMSG_INSTANCE = os.environ.get("ULTRAMSG_INSTANCE", "instance174569")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SYSTEM_PROMPT = """Tu es l'assistant WhatsApp officiel d'Alitech, entreprise spécialisée dans les services Apple iOS à Paris, Bruxelles et Île-de-France. Fondée par Ali, expert Apple avec plus de 5 ans d'expérience et plus de 2000 clients aidés.

SERVICES ET TARIFS :
- Restauration iPhone : 39€ (~60 min) — récupération d'appareils bloqués, données préservées
- Sauvegarde iCloud : 19€ (~30 min) — sauvegarde locale chiffrée + cloud
- Mise à jour iOS : 15€ (~30 min) — mise à jour sécurisée avec sauvegarde préventive
- Récupération Apple ID : 25€ (~45 min) — récupération mot de passe et déverrouillage iCloud
- Transfert de données : 20€ (~45 min) — migration iPhone ou Android

GARANTIES :
- Diagnostic GRATUIT, réponse en 30 minutes
- Satisfait ou remboursé
- Garantie 60 jours sur les restaurations
- Confidentialité totale (aucun accès à vos données personnelles)
- Interventions à distance disponibles

CONTACT :
- Téléphone : 07 68 14 35 36
- Email : contact@alitechs.fr
- Site : https://alitechs.fr
- Horaires : Lundi–Samedi, 9h–19h
- Paiement : CB, Apple Pay, espèces

Réponds toujours en français, de façon professionnelle, chaleureuse et concise.
Si le client a une question complexe ou urgente, invite-le à appeler le 07 68 14 35 36.
Ne réponds qu'aux sujets liés aux services Alitech."""

claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

conversation_history = {}


def send_whatsapp_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE}/messages/chat"
    payload = {"token": ULTRAMSG_TOKEN, "to": to, "body": message}
    requests.post(url, json=payload)


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json or {}
    data = payload.get("data", payload)

    if data.get("type") != "chat":
        return jsonify({"status": "ok"})

    if data.get("fromMe", False):
        return jsonify({"status": "ok"})

    from_number = data.get("from", "")
    body = data.get("body", "").strip()

    if not from_number or not body:
        return jsonify({"status": "ok"})

    if from_number not in conversation_history:
        conversation_history[from_number] = []

    conversation_history[from_number].append({"role": "user", "content": body})

    if len(conversation_history[from_number]) > 10:
        conversation_history[from_number] = conversation_history[from_number][-10:]

    response = claude_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=conversation_history[from_number],
    )

    ai_response = response.content[0].text

    conversation_history[from_number].append(
        {"role": "assistant", "content": ai_response}
    )

    send_whatsapp_message(from_number, ai_response)

    return jsonify({"status": "ok"})


@app.route("/", methods=["GET"])
def home():
    return "Alitech WhatsApp Bot actif ✅"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
