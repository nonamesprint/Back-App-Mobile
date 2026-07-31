import os
import django
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.apps import apps
from django.db import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')
django.setup()

print("🔄 Migration de TOUS les médias vers Supabase...")

# Récupérer tous les modèles avec des champs ImageField ou FileField
all_models = []
for app_config in apps.get_app_configs():
    for model in app_config.get_models():
        fields = []
        for field in model._meta.get_fields():
            if isinstance(field, (models.ImageField, models.FileField)):
                fields.append(field.name)
        if fields:
            all_models.append((model, fields))
            print(f"📦 {app_config.label}.{model.__name__} -> {', '.join(fields)}")

print("\n" + "=" * 60)

total_migrated = 0
for model, fields in all_models:
    print(f"\n📦 {model.__name__}")
    
    for obj in model.objects.all():
        obj_identifier = str(obj)
        for field_name in fields:
            field = getattr(obj, field_name)
            if field and field.name:
                try:
                    local_path = field.path
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            default_storage.save(field.name, ContentFile(f.read()))
                        print(f"   ✅ {field_name} migré pour {obj_identifier}")
                        total_migrated += 1
                    else:
                        print(f"   ⚠️  Fichier introuvable: {local_path}")
                except Exception as e:
                    print(f"   ❌ Erreur {field_name} pour {obj_identifier}: {e}")

print("\n" + "=" * 60)
print(f"✅ Migration terminée ! {total_migrated} fichiers migrés.")