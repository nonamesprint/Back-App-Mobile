# from django.apps import AppConfig


# class PlantesConfig(AppConfig):
#     name = "plantes"

from django.apps import AppConfig

class PlantesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plantes'

    def ready(self):
        import plantes.signals  
        

# class BlogConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'plantes'

#     def ready(self):
#         import plantes.blog_signals # ✅ Active le signal
#         print("✅ Signal des articles activé !")  # ← DOIT APPARAÎTRE