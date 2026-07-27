#!/usr/bin/env python
# diagnostic.py - Script de diagnostic pour les notifications push

import os
import sys
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from django.apps import apps
from django.contrib.auth.models import User
from plantes.models import Article, PushToken
from plantes.notif_services import send_push_notification_to_all_users

print("=" * 60)
print("🔍 DIAGNOSTIC DES NOTIFICATIONS PUSH")
print("=" * 60)
print()

# 1. Vérification des applications
print("📦 1. VÉRIFICATION DES APPLICATIONS")
print("-" * 40)
installed_apps = [app.name for app in apps.get_app_configs()]
print(f"✅ Applications installées : {', '.join(installed_apps)}")
print()

# 2. Vérification du signal
print("📡 2. VÉRIFICATION DU SIGNAL")
print("-" * 40)
try:
    from plantes import blog_signals
    print("✅ blog_signals importé avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import blog_signals : {e}")
print()

# 3. Vérification des modèles
print("📊 3. VÉRIFICATION DES MODÈLES")
print("-" * 40)
try:
    article_count = Article.objects.count()
    print(f"✅ Article : {article_count} articles en base")
except Exception as e:
    print(f"❌ Erreur Article : {e}")

try:
    token_count = PushToken.objects.count()
    print(f"✅ PushToken : {token_count} tokens en base")
except Exception as e:
    print(f"❌ Erreur PushToken : {e}")
print()

# 4. Vérification des tokens actifs
print("🔑 4. VÉRIFICATION DES TOKENS ACTIFS")
print("-" * 40)
active_tokens = PushToken.objects.filter(is_active=True)
if active_tokens.exists():
    print(f"✅ {active_tokens.count()} tokens actifs trouvés")
    for token in active_tokens[:3]:
        print(f"   - Utilisateur: {token.user.username} | Token: {token.token[:20]}...")
else:
    print("❌ Aucun token actif trouvé !")
    print("   → Les utilisateurs doivent se connecter pour générer un token")
print()

# 5. Test de la fonction d'envoi
print("📤 5. TEST DE LA FONCTION D'ENVOI")
print("-" * 40)
print("🧪 Envoi d'une notification de test...")
result = send_push_notification_to_all_users(
    title="🧪 Test de diagnostic",
    body="Ceci est un test automatique",
    data={"test": True}
)
print(f"Résultat : {result}")
print()

# 6. Vérification de l'URL
print("🔗 6. VÉRIFICATION DE L'URL")
print("-" * 40)
from django.urls import reverse, resolve
try:
    url = reverse('register_push_token')
    print(f"✅ URL register-token : {url}")
except Exception as e:
    print(f"❌ Erreur URL : {e}")
print()

# 7. Vérification de l'import requests
print("📦 7. VÉRIFICATION DE LA LIBRAIRIE REQUESTS")
print("-" * 40)
try:
    import requests
    print(f"✅ requests version : {requests.__version__}")
except ImportError as e:
    print(f"❌ requests non installé : {e}")
print()

print("=" * 60)
print("📋 RÉSULTAT DU DIAGNOSTIC")
print("=" * 60)
print()
print("🔧 Si tout est OK, le problème vient du déclenchement du signal.")
print("   Vérifie que le signal est bien connecté à post_save de Article.")
print()
print("🔧 Si 'Aucun token actif trouvé', connecte-toi à l'app pour générer un token.")
print()
print("🔧 Si 'requests non installé', exécute : pip install requests")
