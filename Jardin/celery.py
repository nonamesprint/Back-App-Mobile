# Jardin/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Jardin.settings')

app = Celery('Jardin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ✅ Planification des tâches
app.conf.beat_schedule = {
    'envoyer-rappels-reservations': {
        'task': 'reservations.tasks.envoyer_rappels_reservations_task',
        'schedule': crontab(minute='*/5'),  # ✅ Toutes les 5 minutes
    },
    'nettoyer-anciens-tokens': {
        'task': 'plantes.tasks.nettoyer_tokens_inactifs',
        'schedule': crontab(hour=2, minute=0),  # ✅ Tous les jours à 2h
    },
}

app.conf.timezone = 'UTC'
