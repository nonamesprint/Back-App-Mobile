
# plantes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Article, Abonne

@receiver(post_save, sender=Article)
def notify_subscribers_on_article_creation(sender, instance, created, **kwargs):
    """Envoyer une notification aux abonnés lors de la création d'un nouvel article"""
    
    # Vérifier que l'article est publié
    if not instance.est_publie:
        return
    
    # Si l'article vient d'être créé OU s'il vient d'être publié
    if created or (not created and instance.est_publie):
        # Récupérer tous les abonnés actifs
        abonnes = Abonne.objects.filter(est_actif=True)
        
        if not abonnes.exists():
            print("📧 Aucun abonné actif")
            return
        
        # Nombre d'abonnés
        total = abonnes.count()
        print(f"📧 Envoi de notifications à {total} abonné(s)")
        
        # Liste des emails
        emails = [abonne.email for abonne in abonnes]
        
        # Préparer le sujet
        subject = f"📝 Nouvel article : {instance.titre}"
        
        # Préparer le message
        message = render_to_string('emails/article_notification_email.txt', {
            'article': instance,
            'site_url': 'http://192.168.43.171:8000',
        })
        
        # Envoyer les emails
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                emails,
                fail_silently=False,
            )
            print(f"✅ Notification envoyée à {total} abonné(s)")
        except Exception as e:
            print(f"❌ Erreur envoi notifications: {e}")