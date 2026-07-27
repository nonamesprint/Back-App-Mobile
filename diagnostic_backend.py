# # diagnostic_backend.py
# import django
# import os

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')  # Remplacez
# django.setup()

# from plantes.models import Plante  # Remplacez 'votre_app'
# from django.db import connection

# print("🔍 DIAGNOSTIC DU BACKEND\n")

# # 1. Nombre total de plantes
# total = Plante.objects.count()
# print(f"📊 Total de plantes: {total}")

# # 2. Plantes actives
# actives = Plante.objects.filter(est_active=True).count()
# print(f"✅ Plantes actives: {actives}")

# # 3. Plantes inactives
# inactives = Plante.objects.filter(est_active=False).count()
# print(f"❌ Plantes inactives: {inactives}")

# # 4. Vérifier les noms de champs
# if total > 0:
#     plante = Plante.objects.first()
#     print(f"\n🔍 Structure d'une plante:")
#     print(f"  - ID: {plante.id}")
#     print(f"  - nom_commun_fr: {plante.nom_commun_fr}")
#     print(f"  - nom_scientifique: {plante.nom_scientifique}")
#     print(f"  - est_active: {plante.est_active}")
#     print(f"  - Champs disponibles: {[f.name for f in Plante._meta.get_fields()]}")
# else:
#     print("\n⚠️ Aucune plante dans la base de données !")

# # 5. Requête SQL brute
# print(f"\n🔍 Requête qui sera exécutée:")
# print("SELECT * FROM votre_app_plante WHERE est_active = 1;")


# import os
# import sys
# import django

# sys.path.append('.')
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
# django.setup()

# from django.conf import settings
# from django.core.files.storage import default_storage
# from plantes.models import Plante  # Remplacez 'votre_app'

# print("=" * 60)
# print("🔍 DIAGNOSTIC COMPLET DES MÉDIAS")
# print("=" * 60)

# # 1. Configuration
# print("\n📁 1. CONFIGURATION:")
# print(f"  MEDIA_ROOT: {settings.MEDIA_ROOT}")
# print(f"  MEDIA_URL: {settings.MEDIA_URL}")
# print(f"  DEBUG: {settings.DEBUG}")

# # 2. Dossiers
# print("\n📂 2. DOSSIERS:")
# media_root = settings.MEDIA_ROOT
# print(f"  media existe: {os.path.exists(media_root)}")
# print(f"  media/plantes existe: {os.path.exists(os.path.join(media_root, 'plantes'))}")

# # 3. Fichiers
# print("\n📄 3. FICHIERS DANS media/plantes/:")
# plantes_dir = os.path.join(media_root, 'plantes')
# if os.path.exists(plantes_dir):
#     files = os.listdir(plantes_dir)
#     for f in files:
#         print(f"  - {f}")
# else:
#     print("  ❌ Le dossier media/plantes/ n'existe pas !")

# # 4. Plantes dans la base de données
# print("\n🌿 4. PLANTES DANS LA BDD:")
# for p in Plante.objects.all():
#     print(f"  - {p.nom_commun_fr}")
#     print(f"    Image: {p.image_principale}")
#     if p.image_principale:
#         full_path = os.path.join(settings.MEDIA_ROOT, str(p.image_principale))
#         print(f"    Chemin: {full_path}")
#         print(f"    Existe: {os.path.exists(full_path)}")

# # 5. Tester les URLs
# print("\n🔗 5. TEST DES URLs:")
# url = settings.MEDIA_URL + 'plantes/ja1.jpeg'
# print(f"  URL complète: http://192.168.43.171:8000{url}")

# print("\n" + "=" * 60)
# print("💡 SOLUTIONS POSSIBLES:")
# print("  1. Vérifiez que les fichiers existent dans media/plantes/")
# print("  2. Vérifiez que urls.py contient: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)")
# print("  3. Redémarrez Django: python manage.py runserver 0.0.0.0:8000")
# print("=" * 60)


# from plantes.models import Plante  # Remplacez 'votre_app'

# for plante in Plante.objects.all():
#     if not plante.qr_code:
#         print(f"🔄 Génération QR Code pour: {plante.nom_commun_fr}")
#         plante.generate_qr_code()
#         plante.save()
#         print(f"✅ QR Code généré pour: {plante.nom_commun_fr}")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de mise à jour des QR Codes
Exécution: python manage.py runscript update_qr_codes
Ou: python update_qr_codes.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from plantes.models import Plante

def update_all_qr_codes():
    """Met à jour tous les QR Codes avec la nouvelle URL locale"""
    
    print("\n" + "="*60)
    print("🔄 MISE À JOUR DES QR CODES")
    print("="*60 + "\n")
    
    # URL de base locale
    BASE_URL = "http://192.168.43.171:8000/plante/"
    
    # Compter les plantes
    total = Plante.objects.count()
    print(f"📊 {total} plante(s) trouvée(s)\n")
    
    updated = 0
    errors = 0
    
    for plante in Plante.objects.all():
        try:
            # Ancienne URL
            ancienne = plante.qr_code_url or "Aucune"
            
            # Nouvelle URL
            nouvelle = f"{BASE_URL}{plante.slug}/"
            
            # Mettre à jour
            plante.qr_code_url = nouvelle
            plante.generate_qr_code()
            plante.save()
            
            updated += 1
            print(f"✅ {updated:2d}. {plante.nom_commun_fr}")
            print(f"   Ancienne: {ancienne}")
            print(f"   Nouvelle: {nouvelle}\n")
            
        except Exception as e:
            errors += 1
            print(f"❌ Erreur pour {plante.nom_commun_fr}: {e}\n")
    
    # Résumé
    print("="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    print(f"✅ Succès: {updated} plante(s)")
    print(f"❌ Erreurs: {errors} plante(s)")
    print("\n🎯 Nouvelle URL de base:", BASE_URL)
    print("="*60 + "\n")

if __name__ == "__main__":
    update_all_qr_codes()
