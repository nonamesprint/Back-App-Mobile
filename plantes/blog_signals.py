# # from django.db.models.signals import post_save
# # from django.dispatch import receiver
# # from .models import Article
# # from .notif_services import send_push_notification_to_all_users

# # @receiver(post_save, sender=Article)
# # def notify_new_article(sender, instance, created, **kwargs):
# #     """Déclenche une notification push quand un nouvel article est créé."""
# #     if created:
# #         print(f"📝 Nouvel article détecté : {instance.titre}")
        
# #         send_push_notification_to_all_users(
# #             title=f"📰 Nouvel article : {instance.titre}",
# #             body=instance.extrait[:100] if instance.extrait else "Cliquez pour lire l'article",
# #             data={
# #                 "screen": "ArticleDetail",
# #                 "article_id": instance.id,
# #                 "type": "blog"
# #             }
# #         )


# # plantes/blog_signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Article
# from .notif_services import send_push_notification_to_all_users

# print("🔌 Chargement du signal blog_signals")  # ✅ AJOUTER CETTE LIGNE

# @receiver(post_save, sender=Article)
# def notify_new_article(sender, instance, created, **kwargs):
#     print(f"🔔 SIGNAL DÉCLENCHÉ ! created={created}")  # ✅ AJOUTER CETTE LIGNE
#     if created:
#         print(f"📝 Nouvel article détecté : {instance.titre}")
#         send_push_notification_to_all_users(...)