# plantes/models.py
from django.utils import timezone  
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class Reservation(models.Model):
    # Types de visite
    TYPE_VISITE_CHOICES = [
        ('libre', 'Visite Libre'),
        ('guidee', 'Visite Guidée Standard'),
        ('scolaire', 'Visite Scolaire'),
        ('scientifique', 'Visite Scientifique'),
        ('privatisation', 'Privatisation'),
    ]
    
    # Statuts de réservation
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('annulee', 'Annulée'),
        ('terminee', 'Terminée'),
    ]
    
    # Informations client
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    nombre_personnes = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(50)])
    
    # Détails de la visite
    type_visite = models.CharField(max_length=20, choices=TYPE_VISITE_CHOICES, default='libre')
    date_visite = models.DateField()
    heure_visite = models.TimeField()
    duree_estimee = models.CharField(max_length=50, blank=True, null=True)
    
    # Informations supplémentaires
    message = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    # Métadonnées
    reference = models.CharField(max_length=20, unique=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    rappel_envoye = models.BooleanField(default=False)
    date_rappel = models.DateTimeField(blank=True, null=True)
    
      # plantes/models.py - Méthode save corrigée
    def save(self, *args, **kwargs):
     if not self.reference:
        # Générer une référence unique en utilisant l'année et un compteur
        year = timezone.now().year
        
        # Récupérer la dernière référence créée pour l'année
        last_reservation = Reservation.objects.filter(
            reference__startswith=f'RES-{year}-'
        ).order_by('-reference').first()
        
        if last_reservation:
            # Extraire le numéro de la dernière référence
            last_num = int(last_reservation.reference.split('-')[-1])
            new_num = last_num + 1
        else:
            new_num = 1
        
        self.reference = f"RES-{year}-{str(new_num).zfill(4)}"
    
     super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.nom} ({self.date_visite})"
    
    class Meta:
        ordering = ['-date_creation']
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
