
"""
Script de vérification des QR Codes
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from plantes.models import Plante

print("\n📋 VÉRIFICATION DES QR CODES")
print("="*60)

BASE_URL = "http://192.168.43.171:8000/plante/"
total = Plante.objects.count()
ok = 0
ko = 0

for plante in Plante.objects.all():
    url = plante.qr_code_url or ""
    if url.startswith(BASE_URL):
        print(f"✅ {plante.nom_commun_fr}: {url}")
        ok += 1
    else:
        print(f"❌ {plante.nom_commun_fr}: {url}")
        ko += 1

print("="*60)
print(f"✅ Corrects: {ok}/{total}")
print(f"❌ Incorrects: {ko}/{total}")
print("="*60 + "\n")


