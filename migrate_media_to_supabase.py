#!/usr/bin/env python
# migrate_media_to_supabase.py
"""
Script de migration des médias vers Supabase Storage
Exécution: python migrate_media_to_supabase.py
"""
import os
import sys
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

from plantes.models import Plante

def migrate_plante_media(plante, stats):
    """Migre les médias d'une plante vers Supabase Storage"""
    print(f"\n🌿 {plante.nom_scientifique} (slug: {plante.slug})")
    
    # 1. Migrer l'image principale
    if plante.image_principale and plante.image_principale.name:
        local_path = plante.image_principale.path
        if os.path.exists(local_path):
            try:
                with open(local_path, 'rb') as f:
                    file_content = ContentFile(f.read())
                    saved_name = default_storage.save(plante.image_principale.name, file_content)
                print(f"   ✅ Image migrée: {plante.image_principale.name}")
                stats['images_migrees'] += 1
            except Exception as e:
                print(f"   ❌ Erreur image: {e}")
                stats['erreurs'] += 1
        else:
            print(f"   ⚠️  Image introuvable: {local_path}")
            stats['images_manquantes'] += 1
    else:
        print(f"   ℹ️  Aucune image principale")
    
    # 2. Migrer le QR code
    if plante.qr_code and plante.qr_code.name:
        local_path = plante.qr_code.path
        if os.path.exists(local_path):
            try:
                with open(local_path, 'rb') as f:
                    file_content = ContentFile(f.read())
                    saved_name = default_storage.save(plante.qr_code.name, file_content)
                print(f"   ✅ QR Code migré: {plante.qr_code.name}")
                stats['qr_migres'] += 1
            except Exception as e:
                print(f"   ❌ Erreur QR Code: {e}")
                stats['erreurs'] += 1
        else:
            print(f"   ⚠️  QR Code introuvable: {local_path}")
            stats['qr_manquants'] += 1
    else:
        print(f"   ℹ️  Aucun QR code")
    
    # 3. Mettre à jour l'URL du QR code
    if plante.slug:
        base_url = getattr(settings, 'BASE_URL', settings.BASE_URL)
        new_url = f"{base_url.rstrip('/')}/plante/{plante.slug}"
        if plante.qr_code_url != new_url:
            plante.qr_code_url = new_url
            plante.save(update_fields=['qr_code_url'])
            print(f"   ✅ QR Code URL mise à jour: {new_url}")

def main():
    print("=" * 70)
    print("🔄 MIGRATION DES MÉDIAS VERS SUPABASE STORAGE")
    print("=" * 70)
    print(f"🌍 Environnement: {settings.ENVIRONMENT}")
    print(f"📦 Stockage: {settings.DEFAULT_FILE_STORAGE}")
    print("=" * 70)
    
    # Vérifier l'environnement
    if settings.ENVIRONMENT != 'production':
        print("⚠️  Ce script doit être exécuté en production !")
        print("   Utilisez: DJANGO_ENV=production python migrate_media_to_supabase.py")
        return
    
    # Vérifier les variables S3
    s3_vars = {
        'AWS_ACCESS_KEY_ID': settings.AWS_ACCESS_KEY_ID,
        'AWS_SECRET_ACCESS_KEY': settings.AWS_SECRET_ACCESS_KEY,
        'AWS_STORAGE_BUCKET_NAME': settings.AWS_STORAGE_BUCKET_NAME,
        'AWS_S3_ENDPOINT_URL': settings.AWS_S3_ENDPOINT_URL,
    }
    
    missing = [k for k, v in s3_vars.items() if not v]
    if missing:
        print(f"❌ Variables S3 manquantes: {', '.join(missing)}")
        return
    
    print("\n✅ Variables S3 configurées\n")
    
    # Statistiques
    stats = {
        'images_migrees': 0,
        'qr_migres': 0,
        'images_manquantes': 0,
        'qr_manquants': 0,
        'erreurs': 0
    }
    
    # Migrer les plantes
    plantes = Plante.objects.all()
    print(f"📊 {plantes.count()} plantes à traiter\n")
    
    for plante in plantes:
        migrate_plante_media(plante, stats)
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DE LA MIGRATION")
    print("=" * 70)
    print(f"✅ Images migrées: {stats['images_migrees']}")
    print(f"✅ QR Codes migrés: {stats['qr_migres']}")
    print(f"⚠️  Images manquantes: {stats['images_manquantes']}")
    print(f"⚠️  QR Codes manquants: {stats['qr_manquants']}")
    print(f"❌ Erreurs: {stats['erreurs']}")
    print("=" * 70)
    
    if stats['erreurs'] > 0:
        print("⚠️  Des erreurs sont survenues. Vérifiez les logs ci-dessus.")
    else:
        print("✅ Migration terminée avec succès !")
    print("=" * 70)

if __name__ == "__main__":
    main()