from django.contrib import admin
from .models import Reservation
from django.utils.html import mark_safe
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Reservation
from plantes.export_utils import export_to_csv, export_to_excel, export_to_pdf

# --- Export des Réservations ---
def export_reservations_csv(modeladmin, request, queryset):
    fields = ['reference', 'nom', 'email', 'telephone', 'type_visite', 'date_visite', 'statut']
    headers = ['Référence', 'Nom', 'Email', 'Téléphone', 'Type visite', 'Date visite', 'Statut']
    return export_to_csv(queryset, fields, headers)
export_reservations_csv.short_description = "📊 Exporter en CSV"

def export_reservations_excel(modeladmin, request, queryset):
    fields = ['reference', 'nom', 'email', 'telephone', 'type_visite', 'date_visite', 'statut']
    headers = ['Référence', 'Nom', 'Email', 'Téléphone', 'Type visite', 'Date visite', 'Statut']
    return export_to_excel(queryset, fields, headers, 'Réservations')
export_reservations_excel.short_description = "📊 Exporter en Excel"

def export_reservations_pdf(modeladmin, request, queryset):
    fields = ['reference', 'nom', 'email', 'telephone', 'type_visite', 'date_visite', 'statut']
    headers = ['Réf.', 'Nom', 'Email', 'Téléphone', 'Type', 'Date', 'Statut']
    return export_to_pdf(queryset, fields, headers, "Liste des Réservations")
export_reservations_pdf.short_description = "📊 Exporter en PDF"


# ==================== ADMIN RESERVATION ====================
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reference', 'nom', 'email', 'type_visite', 'date_visite', 'heure_visite', 'statut', 'date_creation')
    list_filter = ('type_visite', 'statut', 'date_visite')
    search_fields = ('reference', 'nom', 'email', 'telephone')
    readonly_fields = ('reference', 'date_creation', 'date_modification')
    actions = [
        'confirmer_reservations', 
        'annuler_reservations',
        export_reservations_csv, 
        export_reservations_excel, 
        export_reservations_pdf
    ]
    fieldsets = (
        ('Informations client', {
            'fields': ('nom', 'email', 'telephone', 'nombre_personnes')
        }),
        ('Détails de la visite', {
            'fields': ('type_visite', 'date_visite', 'heure_visite', 'duree_estimee')
        }),
        ('Informations supplémentaires', {
            'fields': ('message', 'statut')
        }),
        ('Métadonnées', {
            'fields': ('reference', 'date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )
    
    def confirmer_reservations(self, request, queryset):
        """Action pour confirmer les réservations sélectionnées"""
        count = 0
        for reservation in queryset:
            if reservation.statut == 'en_attente':
                reservation.statut = 'confirmee'
                reservation.save()
                count += 1
                
                # Envoyer l'email de confirmation
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
        
        if count > 0:
            self.message_user(request, f"✅ {count} réservation(s) confirmée(s) avec succès.")
        else:
            self.message_user(request, "⚠️ Aucune réservation en attente n'a été trouvée.", level=messages.WARNING)
    confirmer_reservations.short_description = "✅ Confirmer les réservations sélectionnées"
    
    def annuler_reservations(self, request, queryset):
        """Action pour annuler les réservations sélectionnées"""
        count = 0
        for reservation in queryset:
            if reservation.statut not in ['annulee', 'terminee']:
                reservation.statut = 'annulee'
                reservation.save()
                count += 1
                
                # Envoyer l'email d'annulation
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
        
        if count > 0:
            self.message_user(request, f"❌ {count} réservation(s) annulée(s) avec succès.")
        else:
            self.message_user(request, "⚠️ Aucune réservation à annuler n'a été trouvée.", level=messages.WARNING)
    annuler_reservations.short_description = "❌ Annuler les réservations sélectionnées"
    

admin.site.register(Reservation, ReservationAdmin)
