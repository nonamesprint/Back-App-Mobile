# reservations/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Reservation
from plantes.notif_services import send_push_notification_to_all_users

@shared_task
def envoyer_rappels_reservations_task():
    """Tâche Celery pour envoyer les rappels de réservation."""
    now = timezone.now()
    dans_30_minutes = now + timedelta(minutes=30)
    
    print(f"🔔 Vérification des rappels à {now}")
    
    # ✅ Récupérer les réservations non rappelées
    reservations = Reservation.objects.filter(
        rappel_envoye=False,
        statut__in=['confirmée']
    )
    
    rappels_a_envoyer = []
    for reservation in reservations:
        date_visite = reservation.date_visite
        heure_visite = reservation.heure_visite
        
        # ✅ Créer un datetime avec fuseau horaire
        heure_datetime = timezone.make_aware(
            timezone.datetime.combine(date_visite, heure_visite)
        )
        
        # ✅ Vérifier si la visite est dans les 30 minutes
        if now <= heure_datetime <= dans_30_minutes:
            rappels_a_envoyer.append(reservation)
    
    print(f"🔔 {len(rappels_a_envoyer)} rappel(s) à envoyer")
    
    for reservation in rappels_a_envoyer:
        # Envoyer la notification
        send_push_notification_to_all_users(
            title=f"🌿 Rappel de visite",
            body=f"Votre visite du {reservation.date_visite} à {reservation.heure_visite} est dans 30 minutes.",
            data={
                "screen": "Reservations",
                "reservation_id": reservation.id,
                "type": "rappel"
            }
        )
        
        # Marquer le rappel comme envoyé
        reservation.rappel_envoye = True
        reservation.date_rappel = now
        reservation.save()
        
        print(f"✅ Rappel envoyé pour la réservation #{reservation.id}")
    
    return f"{len(rappels_a_envoyer)} rappel(s) envoyés"


@shared_task
def test_envoyer_rappel_immmediat(reservation_id):
    """Test : envoie un rappel immédiat pour une réservation spécifique."""
    from .models import Reservation
    from plantes.notif_services import send_push_notification_to_all_users
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        
        send_push_notification_to_all_users(
            title=f"🌿 TEST - Rappel de visite",
            body=f"Test immédiat pour {reservation.nom} - {reservation.date_visite} à {reservation.heure_visite}",
            data={
                "screen": "Reservations",
                "reservation_id": reservation.id,
                "type": "test"
            }
        )
        
        print(f"✅ Test envoyé pour la réservation #{reservation.id}")
        return f"Test envoyé pour #{reservation.id}"
    except Reservation.DoesNotExist:
        return "Réservation non trouvée"