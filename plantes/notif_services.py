 
import requests
from .models import PushToken

def send_push_notification_to_all_users(title, body, data=None):
    """Envoie une notification à tous les utilisateurs ayant un token actif."""
    tokens = PushToken.objects.filter(is_active=True)
    
    if not tokens.exists():
        print("🔕 Aucun token actif trouvé.")
        return

    # ✅ Message pour Expo
    messages = []
    for token in tokens:
        messages.append({
            "to": token.token,
            "sound": "default",
            "title": title,
            "body": body,
            "data": data or {},
        })

    # ✅ Envoi groupé à l'API Expo
    try:
        response = requests.post(
            "https://exp.host/--/api/v2/push/send",
            json=messages,
            headers={"Accept": "application/json"}
        )
        print(f"📤 Notification envoyée à {len(messages)} utilisateur(s)")
        return response.json()
    except Exception as e:
        print(f"❌ Erreur envoi notification: {e}")
        return None