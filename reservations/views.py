
# plantes/views.py
from .models import *
from django.shortcuts import render
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .serializers import*
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated



# ==================== RESERVATION VIEWSET ====================
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    # permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    # ✅ AJOUTEZ CETTE MÉTHODE
    def get_permissions(self):
        """
        Définit les permissions selon l'action :
        - create, disponibilites, creneaux : Public (AllowAny)
        - Toutes les autres actions : Authentifié (IsAuthenticated)
        """
        if self.action in ['create', 'disponibilites', 'creneaux']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        """Créer une réservation et envoyer un email"""
        reservation = serializer.save()
        
        # Envoyer un email de confirmation de création
        try:
            subject = f"📅 Demande de réservation - {reservation.reference}"
            message = render_to_string('emails/reservation_creation_email.txt', {
                'reservation': reservation
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )
            print(f"📧 Email de création envoyé à {reservation.email}")
        except Exception as e:
            print(f"❌ Erreur envoi email création: {e}")
        
        return reservation
    
    @action(detail=False, methods=['get'])
    def disponibilites(self, request):
        """Vérifier les disponibilités pour une date donnée"""
        date_str = request.query_params.get('date')
        type_visite = request.query_params.get('type_visite', 'libre')
        
        if not date_str:
            return Response(
                {'error': 'Veuillez spécifier une date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limites de réservation par type
        limites = {
            'libre': 50,
            'guidee': 20,
            'scolaire': 30,
            'scientifique': 15,
            'privatisation': 100,
        }
        
        # Compter les réservations existantes pour ce jour
        count = Reservation.objects.filter(
            date_visite=date,
            type_visite=type_visite,
            statut__in=['en_attente', 'confirmee']
        ).count()
        
        limite = limites.get(type_visite, 50)
        disponible = count < limite
        places_restantes = limite - count
        
        return Response({
            'date': date_str,
            'type_visite': type_visite,
            'total_reservations': count,
            'limite': limite,
            'places_restantes': places_restantes,
            'disponible': disponible,
        })
    
    @action(detail=False, methods=['get'])
    def creneaux(self, request):
        """Récupérer les créneaux disponibles pour une date donnée"""
        date_str = request.query_params.get('date')
        type_visite = request.query_params.get('type_visite', 'libre')
        
        if not date_str:
            return Response(
                {'error': 'Veuillez spécifier une date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Format de date invalide. Utilisez YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ Définir les créneaux avec plages horaires
        if type_visite == 'libre':
            creneaux = [
                {'id': '1', 'heure': '08:00 - 10:00', 'debut': '08:00', 'fin': '10:00', 'disponible': True},
                {'id': '2', 'heure': '10:00 - 12:00', 'debut': '10:00', 'fin': '12:00', 'disponible': True},
                {'id': '3', 'heure': '12:00 - 14:00', 'debut': '12:00', 'fin': '14:00', 'disponible': True},
                {'id': '4', 'heure': '14:00 - 16:00', 'debut': '14:00', 'fin': '16:00', 'disponible': True},
                {'id': '5', 'heure': '16:00 - 18:00', 'debut': '16:00', 'fin': '18:00', 'disponible': True},
            ]
        elif type_visite == 'guidee':
            creneaux = [
                {'id': '1', 'heure': '09:00 - 11:00', 'debut': '09:00', 'fin': '11:00', 'disponible': True},
                {'id': '2', 'heure': '11:00 - 13:00', 'debut': '11:00', 'fin': '13:00', 'disponible': True},
                {'id': '3', 'heure': '14:00 - 16:00', 'debut': '14:00', 'fin': '16:00', 'disponible': True},
                {'id': '4', 'heure': '16:00 - 18:00', 'debut': '16:00', 'fin': '18:00', 'disponible': True},
            ]
        elif type_visite == 'scolaire':
            creneaux = [
                {'id': '1', 'heure': '09:00 - 11:00', 'debut': '09:00', 'fin': '11:00', 'disponible': True},
                {'id': '2', 'heure': '11:00 - 13:00', 'debut': '11:00', 'fin': '13:00', 'disponible': True},
                {'id': '3', 'heure': '14:00 - 16:00', 'debut': '14:00', 'fin': '16:00', 'disponible': True},
            ]
        elif type_visite == 'scientifique':
            creneaux = [
                {'id': '1', 'heure': '09:00 - 12:00', 'debut': '09:00', 'fin': '12:00', 'disponible': True},
                {'id': '2', 'heure': '14:00 - 17:00', 'debut': '14:00', 'fin': '17:00', 'disponible': True},
            ]
        else:  # privatisation
            creneaux = [
                {'id': '1', 'heure': 'Journée complète', 'debut': '08:00', 'fin': '18:00', 'disponible': True},
            ]
        
        # Vérifier les réservations existantes
        reservations = Reservation.objects.filter(
            date_visite=date,
            type_visite=type_visite,
            statut__in=['en_attente', 'confirmee']
        )
        
        # Marquer les créneaux déjà réservés
        for reservation in reservations:
            heure_debut = reservation.heure_visite.strftime('%H:%M')
            for creneau in creneaux:
                if creneau['debut'] == heure_debut:
                    creneau['disponible'] = False
                    break
        
        return Response(creneaux)
    
    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        """Annuler une réservation et envoyer un email"""
        reservation = self.get_object()
        
        if reservation.statut == 'annulee':
            return Response(
                {'error': 'Cette réservation est déjà annulée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if reservation.statut == 'terminee':
            return Response(
                {'error': 'Cette réservation est déjà terminée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.statut = 'annulee'
        reservation.save()
        
        # ✅ Envoyer l'email d'annulation
        try:
            subject = f"❌ Réservation annulée - {reservation.reference}"
            message = render_to_string('emails/annulation_email.txt', {
                'reservation': reservation
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )
            print(f"📧 Email d'annulation envoyé à {reservation.email}")
        except Exception as e:
            print(f"❌ Erreur envoi email annulation: {e}")
        
        return Response({
            'message': 'Réservation annulée avec succès',
            'reference': reservation.reference
        })
    
    @action(detail=True, methods=['post'])
    def confirmer(self, request, pk=None):
        """Confirmer une réservation et envoyer un email"""
        reservation = self.get_object()
        
        if reservation.statut != 'en_attente':
            return Response(
                {'error': f'Cette réservation est déjà {reservation.statut}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.statut = 'confirmee'
        reservation.save()
        
        # ✅ Envoyer l'email de confirmation
        try:
            subject = f"✅ Réservation confirmée - {reservation.reference}"
            message = render_to_string('emails/confirmation_email.txt', {
                'reservation': reservation
            })
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )
            print(f"📧 Email de confirmation envoyé à {reservation.email}")
        except Exception as e:
            print(f"❌ Erreur envoi email confirmation: {e}")
        
        return Response({
            'message': 'Réservation confirmée avec succès',
            'reference': reservation.reference
        })


