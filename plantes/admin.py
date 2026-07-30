# admin.py
from django.contrib import admin
from .models import *
from django.utils.html import mark_safe
from reservations.models import Reservation
from django.contrib import messages
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render
from django.urls import path
from .export_utils import export_stats_to_csv, export_stats_to_excel, export_stats_to_pdf, export_to_csv, export_to_excel, export_to_pdf
from django.conf import settings

# ==================== ACTIONS D'EXPORTATION ====================

# --- Export des Plantes ---
def export_plantes_csv(modeladmin, request, queryset):
    fields = ['id', 'nom_commun_fr', 'nom_scientifique', 'famille_botanique', 
              'zone_geographique', 'est_active', 'date_creation']
    headers = ['ID', 'Nom commun', 'Nom scientifique', 'Famille botanique', 
               'Zone géographique', 'Active', 'Date de création']
    return export_to_csv(queryset, fields, headers)
export_plantes_csv.short_description = "📊 Exporter en CSV"

def export_plantes_excel(modeladmin, request, queryset):
    fields = ['id', 'nom_commun_fr', 'nom_scientifique', 'famille_botanique', 
              'zone_geographique', 'est_active', 'date_creation']
    headers = ['ID', 'Nom commun', 'Nom scientifique', 'Famille botanique', 
               'Zone géographique', 'Active', 'Date de création']
    return export_to_excel(queryset, fields, headers, 'Plantes')
export_plantes_excel.short_description = "📊 Exporter en Excel"

def export_plantes_pdf(modeladmin, request, queryset):
    fields = ['id', 'nom_commun_fr', 'nom_scientifique', 'famille_botanique', 
              'zone_geographique', 'est_active', 'date_creation']
    headers = ['ID', 'Nom commun', 'Nom scientifique', 'Famille', 'Zone', 'Active', 'Date']
    return export_to_pdf(queryset, fields, headers, "Liste des Plantes")
export_plantes_pdf.short_description = "📊 Exporter en PDF"


# --- Export des Articles ---
def export_articles_csv(modeladmin, request, queryset):
    fields = ['titre', 'auteur', 'categorie', 'vues', 'date_publication', 'est_publie']
    headers = ['Titre', 'Auteur', 'Catégorie', 'Vues', 'Date publication', 'Publié']
    return export_to_csv(queryset, fields, headers)
export_articles_csv.short_description = "📊 Exporter en CSV"

def export_articles_excel(modeladmin, request, queryset):
    fields = ['titre', 'auteur', 'categorie', 'vues', 'date_publication', 'est_publie']
    headers = ['Titre', 'Auteur', 'Catégorie', 'Vues', 'Date publication', 'Publié']
    return export_to_excel(queryset, fields, headers, 'Articles')
export_articles_excel.short_description = "📊 Exporter en Excel"

def export_articles_pdf(modeladmin, request, queryset):
    fields = ['titre', 'auteur', 'categorie', 'vues', 'date_publication', 'est_publie']
    headers = ['Titre', 'Auteur', 'Catégorie', 'Vues', 'Date', 'Publié']
    return export_to_pdf(queryset, fields, headers, "Liste des Articles")
export_articles_pdf.short_description = "📊 Exporter en PDF"


# --- Export des Abonnés ---
def export_abonnes_csv(modeladmin, request, queryset):
    fields = ['email', 'nom', 'est_actif', 'date_abonnement']
    headers = ['Email', 'Nom', 'Actif', "Date d'abonnement"]
    return export_to_csv(queryset, fields, headers)
export_abonnes_csv.short_description = "📊 Exporter en CSV"

def export_abonnes_excel(modeladmin, request, queryset):
    fields = ['email', 'nom', 'est_actif', 'date_abonnement']
    headers = ['Email', 'Nom', 'Actif', "Date d'abonnement"]
    return export_to_excel(queryset, fields, headers, 'Abonnés')
export_abonnes_excel.short_description = "📊 Exporter en Excel"

def export_abonnes_pdf(modeladmin, request, queryset):
    fields = ['email', 'nom', 'est_actif', 'date_abonnement']
    headers = ['Email', 'Nom', 'Actif', "Date d'abonnement"]
    return export_to_pdf(queryset, fields, headers, 'Abonnés')
export_abonnes_pdf.short_description = "📊 Exporter en PDF"


# --- Export des Circuits ---
def export_circuits_csv(modeladmin, request, queryset):
    fields = ['titre', 'description', 'duree_estimee', 'points_interet', 'est_active']
    headers = ['Titre', 'Description', 'Durée', "Points d'intérêt", 'Actif']
    return export_to_csv(queryset, fields, headers)
export_circuits_csv.short_description = "📊 Exporter en CSV"

def export_circuits_excel(modeladmin, request, queryset):
    fields = ['titre', 'description', 'duree_estimee', 'points_interet', 'est_active']
    headers = ['Titre', 'Description', 'Durée', "Points d'intérêt", 'Actif']
    return export_to_excel(queryset, fields, headers, 'Circuits')
export_circuits_excel.short_description = "📊 Exporter en Excel"

def export_circuits_pdf(modeladmin, request, queryset):
    fields = ['titre', 'description', 'duree_estimee', 'points_interet', 'est_active']
    headers = ['Titre', 'Description', 'Durée', "Points d'intérêt", 'Actif']
    return export_to_pdf(queryset, fields, headers, 'Circuits')
export_circuits_pdf.short_description = "📊 Exporter en Excel"



# ==================== MIXIN PERMISSIONS BOTANISTE ====================
class BotanistePermissionsMixin:
    """Mixin pour les permissions des botanistes - Accès complet sur Plantes et Articles, vue sur Circuits"""
    
    def has_add_permission(self, request):
        """Peut ajouter : Super Admin + Botaniste"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Botaniste').exists():
            return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Peut modifier : Super Admin + Botaniste"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Botaniste').exists():
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Peut supprimer : Super Admin + Botaniste ✅"""
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name='Botaniste').exists():
            return True
        return False
    
    def has_view_permission(self, request, obj=None):
        """Peut voir : Tout le monde"""
        return True


class PlanteAdmin(admin.ModelAdmin, BotanistePermissionsMixin):
    list_display = ('nom_scientifique', 'nom_commun_fr', 'est_active', 'qr_code_preview','qr_code_url')
    readonly_fields = ('qr_code_preview', 'date_creation',)  # Rendre ces champs en lecture seule
    fieldsets = (
        ('Informations principales', {
            'fields': ('nom_scientifique', 'nom_commun_fr', 'description', 'famille_botanique', 'anecdote', 'zone_geographique',)
        }),
        ('Images', {
            'fields': ('image_principale',)        
        }),
        ('QR Code', {
            'fields': ('qr_code_preview', 'qr_code_url')
        }),
        ('Métadonnées', {
            'fields': ('date_creation',)
        }),
    )
    actions = [export_plantes_csv, export_plantes_excel, export_plantes_pdf]  

    def qr_code_preview(self, obj):
        """Affiche un aperçu du QR Code dans l'admin"""
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="150" height="150" />')
        return "❌ QR Code non généré"
    qr_code_preview.short_description = "Aperçu QR Code"
    
    
    def qr_code_url_display(self, obj):
        """Affiche l'URL complète du QR Code"""
        if obj.qr_code_url:
            # Utiliser la BASE_URL configurée
            if settings.ENVIRONMENT == 'production':
                base_url = settings.BASE_URL
            else:
                base_url = 'http://localhost:8000'
            
            full_url = f"{base_url}{obj.qr_code.url if obj.qr_code else obj.qr_code_url}"
            return mark_safe(f'<a href="{full_url}" target="_blank">{full_url[:60]}...</a>')
        return "❌ Pas d'URL"
    qr_code_url_display.short_description = "URL QR Code"

    def save_model(self, request, obj, form, change):
        """Surcharge pour générer le QR Code à la sauvegarde dans l'admin"""
        # Générer le QR Code avant la sauvegarde
        obj.generate_qr_code(force=True)
        # Sauvegarder l'objet
        super().save_model(request, obj, form, change)
        
    
# ==================== ADMIN CIRCUIT ====================
class CircuitAdmin(admin.ModelAdmin, BotanistePermissionsMixin):
    list_display = ('titre', 'duree_estimee', 'est_active', 'points_interet_count')
    list_filter = ('est_active',)
    search_fields = ('titre', 'description', 'points_interet')
    readonly_fields = ('date_creation', 'date_modification', 'slug')
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'description', 'duree_estimee', 'points_interet')
        }),
        ('Image', {
            'fields': ('image_principale',)
        }),
        ('Métadonnées', {
            'fields': ('est_active', 'slug', 'date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )
    actions = [export_circuits_csv, export_circuits_excel, export_circuits_pdf]  

    def points_interet_count(self, obj):
        if obj.points_interet:
            return len(obj.points_interet.split(','))
        return 0
    points_interet_count.short_description = "Nombre de points d'intérêt"
    
    
# ==================== ADMIN ARTICLE ====================
class ArticleAdmin(admin.ModelAdmin,BotanistePermissionsMixin):
    list_display = ('titre', 'categorie', 'auteur', 'est_publie', 'date_publication', 'vues')
    list_filter = ('est_publie', 'categorie', 'date_publication')
    search_fields = ('titre', 'contenu', 'auteur', 'tags')
    readonly_fields = ('date_creation', 'date_modification', 'vues', 'date_publication')
    prepopulated_fields = {'slug': ('titre',)}
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('titre', 'slug', 'contenu', 'extrait', 'auteur')
        }),
        ('Catégorisation', {
            'fields': ('categorie', 'tags')
        }),
        ('Image', {
            'fields': ('image_principale',)
        }),
        ('Publication', {
            'fields': ('est_publie', 'date_publication')
        }),
        ('Statistiques', {
            'fields': ('vues', 'date_creation', 'date_modification'),
            'classes': ('collapse',),
        }),
    )
    actions = [export_articles_csv, export_articles_excel, export_articles_pdf] 
    
    

# ==================== ADMIN ABONNE ====================
class AbonneAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'est_actif', 'date_abonnement')
    list_filter = ('est_actif', 'date_abonnement')
    search_fields = ('email', 'nom')
    readonly_fields = ('date_abonnement',)
    fieldsets = (
        ('Informations', {
            'fields': ('email', 'nom')
        }),
        ('Statut', {
            'fields': ('est_actif', 'date_abonnement')
        }),
    )
    actions = [export_abonnes_csv, export_abonnes_excel, export_abonnes_pdf]  
    
class ArticleVueAdmin(admin.ModelAdmin):
    list_display = ('article', 'ip_address', 'date_vue')
    list_filter = ('date_vue',)
    search_fields = ('ip_address', 'article__titre')
    readonly_fields = ('date_vue',)




def stats_view(request):
    """Vue pour afficher les statistiques dans l'admin"""
    
    # ===== STATISTIQUES GÉNÉRALES =====
    total_plantes = Plante.objects.filter(est_active=True).count()
    total_circuits = Circuit.objects.filter(est_active=True).count()
    total_articles = Article.objects.filter(est_publie=True).count()
    total_abonnes = Abonne.objects.filter(est_actif=True).count()
    total_reservations = Reservation.objects.count()
    
    plantes_avec_image = Plante.objects.filter(est_active=True, image_principale__isnull=False).exclude(image_principale='').count()
    plantes_avec_qr = Plante.objects.filter(est_active=True, qr_code__isnull=False).exclude(qr_code='').count()
    
    # ===== RÉSERVATIONS =====
    reservations_attente = Reservation.objects.filter(statut='en_attente').count()
    reservations_confirmees = Reservation.objects.filter(statut='confirmee').count()
    reservations_annulees = Reservation.objects.filter(statut='annulee').count()
    reservations_terminees = Reservation.objects.filter(statut='terminee').count()
    
    reservations_par_type = {}
    for type_visite in ['libre', 'guidee', 'scolaire', 'scientifique', 'privatisation']:
        count = Reservation.objects.filter(type_visite=type_visite).count()
        if count > 0:
            reservations_par_type[type_visite] = count
    
    # ===== ARTICLES =====
    articles_populaires = list(Article.objects.filter(est_publie=True).order_by('-vues')[:5].values('id', 'titre', 'vues'))
    total_vues_articles = Article.objects.filter(est_publie=True).aggregate(Sum('vues'))['vues__sum'] or 0
    moyenne_vues = Article.objects.filter(est_publie=True).aggregate(Avg('vues'))['vues__avg'] or 0
    
    # ===== ÉVOLUTION =====
    today = timezone.now().date()
    reservations_jour = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = Reservation.objects.filter(date_creation__date=day).count()
        reservations_jour.append({
            'date': day.strftime('%d/%m'),
            'count': count
        })
    
    week_ago = timezone.now() - timedelta(days=7)
    nouvelles_reservations = Reservation.objects.filter(date_creation__gte=week_ago).count()
    nouveaux_abonnes = Abonne.objects.filter(date_abonnement__gte=week_ago, est_actif=True).count()
    
    # ===== DERNIÈRES RÉSERVATIONS =====
    dernieres_reservations = list(Reservation.objects.all().order_by('-date_creation')[:5].values(
        'reference', 'nom', 'email', 'type_visite', 'date_visite', 'statut'
    ))
    
    # ===== ABONNÉS =====
    abonnes_inactifs = Abonne.objects.filter(est_actif=False).count()
    abonnes_actifs = Abonne.objects.filter(est_actif=True).count()
    nouveaux_abonnes_30j = Abonne.objects.filter(date_abonnement__gte=timezone.now() - timedelta(days=30), est_actif=True).count()
    
    
    # ===== CONTEXTE POUR LE TEMPLATE =====
    context = {
        # Générales
        'total_plantes': total_plantes,
        'total_circuits': total_circuits,
        'total_articles': total_articles,
        'total_abonnes': total_abonnes,
        'total_reservations': total_reservations,
        
        # Plantes
        'plantes_avec_image': plantes_avec_image,
        'plantes_avec_qr': plantes_avec_qr,
        
        # Réservations
        'reservations_attente': reservations_attente,
        'reservations_confirmees': reservations_confirmees,
        'reservations_annulees': reservations_annulees,
        'reservations_terminees': reservations_terminees,
        'reservations_par_type': reservations_par_type,
        'nouvelles_reservations': nouvelles_reservations,
        'dernieres_reservations': dernieres_reservations,
        
        # Articles
        'articles_populaires': articles_populaires,
        'total_vues_articles': total_vues_articles,
        'moyenne_vues': round(moyenne_vues, 1) if moyenne_vues else 0,
        
        # Abonnés
        'abonnes_actifs': abonnes_actifs,
        'abonnes_inactifs': abonnes_inactifs,
        'nouveaux_abonnes': nouveaux_abonnes,
        'nouveaux_abonnes_30j': nouveaux_abonnes_30j,
        
       
        
        # Évolution
        'reservations_jour': reservations_jour,
    }
    
    # ===== EXPORT =====
    export_format = request.GET.get('export')
    
    if export_format == 'excel':
        return export_stats_to_excel(context, "Statistiques du Jardin Botanique")
    elif export_format == 'csv':
        return export_stats_to_csv(context, "Statistiques du Jardin Botanique")
    elif export_format == 'pdf':
        return export_stats_to_pdf(context, "Statistiques du Jardin Botanique")
    
    return render(request, 'admin/stats.html', context)


# ==================== ENREGISTREMENT ====================
# Enregistrer les modèles sur l'admin par défaut
admin.site.register(Plante, PlanteAdmin)
admin.site.register(Circuit, CircuitAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Abonne, AbonneAdmin)
admin.site.register(ArticleVue, ArticleVueAdmin)


# plantes/admin.py
from .models import QuizQuestion, QuizOption, QuizSession, QuizReponse

class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4
    fields = ('texte', 'est_correcte', 'ordre')

class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'niveau', 'points', 'temps_estime', 'est_active')
    list_filter = ('niveau', 'est_active')
    search_fields = ('question',)
    inlines = [QuizOptionInline]
    fieldsets = (
        ('Question', {
            'fields': ('question', 'niveau', 'points', 'temps_estime', 'est_active')
        }),
    )

class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'score_total', 'questions_repondues', 'bonnes_reponses', 'est_termine', 'date_debut')
    list_filter = ('est_termine', 'niveau_actuel')
    readonly_fields = ('date_debut', 'date_fin')

admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(QuizOption)
admin.site.register(QuizSession, QuizSessionAdmin)
admin.site.register(QuizReponse)


# ==================== AJOUTER L'URL STATS ====================
from django.urls import re_path, path

# ✅ Une seule définition de get_urls (sans récursion)
original_get_urls = admin.site.get_urls

def get_urls_with_stats():
    urls = original_get_urls()
    custom_urls = [
        path('stats/', admin.site.admin_view(stats_view), name='stats'),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls_with_stats


# ==================== AJOUTER UN LIEN DANS LE MENU ====================
# Créer un template personnalisé pour le menu
admin.site.index_template = 'admin/index_with_stats.html'


# ==================== PERSONNALISATION DU HEADER ====================
# Modifier le header de l'admin
admin.site.site_header = "🌿 Jardin Botanique - Administration"
admin.site.site_title = "Admin Jardin Botanique"
admin.site.index_title = "📊 Tableau de bord"