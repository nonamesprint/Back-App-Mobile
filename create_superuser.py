import os
import django
from django.contrib.auth import get_user_model

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

User = get_user_model()

# Variables d'environnement pour le superutilisateur
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@jardin.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin')

# Vérifier si le superutilisateur existe déjà
if not User.objects.filter(username=ADMIN_USERNAME).exists():
    User.objects.create_superuser(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)
    print(f"✅ Superutilisateur '{ADMIN_USERNAME}' créé avec succès !")
else:
    print(f"ℹ️  Le superutilisateur '{ADMIN_USERNAME}' existe déjà.")