from io import BytesIO
from django.core.files import File
from django.db import models
from django.utils.text import slugify
import qrcode
from django.conf import settings


class Plante(models.Model):
    # Informations de base
    nom_scientifique = models.CharField(max_length=255, unique=True, help_text="Nom latin unique.")
    nom_commun_fr = models.CharField(max_length=255, help_text="Nom usuel en français.")
    
    # Description et détails
    description = models.TextField(help_text="Description accessible au grand public.")
    famille_botanique = models.CharField(max_length=255)
    zone_geographique = models.CharField(max_length=255, blank=True, null=True)
    anecdote = models.TextField(blank=True, null=True, help_text="Anecdote culturelle ou médicinale.")
    
    # Images (pour le moment, nous stockons les chemins)
    image_principale = models.ImageField(upload_to='plantes/', help_text="Photo principale de la plante.")
    # image_feuille = models.ImageField(upload_to='plantes/', blank=True, null=True)
    # image_fleur = models.ImageField(upload_to='plantes/', blank=True, null=True)
    # image_fruit = models.ImageField(upload_to='plantes/', blank=True, null=True)

    # Système de QR Code
    qr_code_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL unique de la fiche plante pour le QR Code.")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="Image du QR Code générée.")

    # Métadonnées
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Générer un slug unique à partir du nom scientifique
            self.slug = slugify(self.nom_scientifique)
            
        self.generate_qr_code()
        super().save(*args, **kwargs)
        
    def generate_qr_code(self):
        """Génère le QR code et sauvegarde dans le champ qr_code"""
        try:
            # Générer l'URL unique pour la plante
            # base_url = "http://192.168.43.171:8000/plante/"
            
            base_url = settings.BASE_URL.rstrip('/')
            url = f"{base_url}{self.slug}"
            self.qr_code_url = url
            
            # Générer l'image QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarder l'image
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f"qr_{self.slug}.png"
            
            # Supprimer l'ancien QR Code s'il existe
            if self.qr_code:
                try:
                    self.qr_code.delete(save=False)
                except:
                    pass
            
            # Sauvegarder le nouveau QR Code
            self.qr_code.save(file_name, File(buffer), save=False)
            
        except Exception as e:
            print(f"❌ Erreur génération QR Code: {e}")

    def __str__(self):
        return f"{self.nom_commun_fr} ({self.nom_scientifique})"

    def __str__(self):
        return f"{self.nom_scientifique} ({self.nom_commun_fr})"
    
    

class Circuit(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    duree_estimee = models.CharField(max_length=100, help_text="Ex: 2 heures, 1 journée")
    points_interet = models.TextField(help_text="Liste des points d'intérêt séparés par des virgules")
    image_principale = models.ImageField(upload_to='circuits/', blank=True, null=True)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre
    
    class Meta:
        ordering = ['titre']
        


class Article(models.Model):
    titre = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    contenu = models.TextField()
    extrait = models.CharField(max_length=300, help_text="Résumé de l'article pour la liste")
    auteur = models.CharField(max_length=255)
    image_principale = models.ImageField(upload_to='blog/', blank=True, null=True)
    categorie = models.CharField(max_length=100, choices=[
        ('plante_du_mois', '🌿 Plante du mois'),
        ('saison', '🌸 Saisons de floraison'),
        ('actualite', '📰 Actualités scientifiques'),
        ('decouverte', '🔬 Nouvelles découvertes'),
        ('conseil', '💡 Conseils jardinage'),
        ('evenement', '🎪 Événements'),
    ], default='actualite')
    tags = models.CharField(max_length=255, blank=True, help_text="Tags séparés par des virgules")
    est_publie = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    vues = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre
    
    class Meta:
        ordering = ['-date_publication']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        
        

class Abonne(models.Model):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100, blank=True, null=True)
    est_actif = models.BooleanField(default=True)
    date_abonnement = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Abonné'
        verbose_name_plural = 'Abonnés'
        

class ArticleVue(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='vues_detail')
    ip_address = models.GenericIPAddressField()
    date_vue = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('article', 'ip_address') 
        verbose_name = 'Vue d\'article'
        verbose_name_plural = 'Vues d\'articles'
    
    def __str__(self):
        return f"{self.article.titre} - {self.ip_address}"
    

class QuizQuestion(models.Model):
    NIVEAU_CHOICES = [
        ('facile', '🌱 Facile'),
        ('moyen', '🌿 Moyen'),
        ('difficile', '🌳 Difficile'),
    ]
    
    question = models.TextField()
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='facile')
    points = models.PositiveIntegerField(default=10, help_text="Points attribués pour une bonne réponse")
    temps_estime = models.PositiveIntegerField(default=30, help_text="Temps estimé en secondes")
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.question[:50]}... ({self.get_niveau_display()})"
    
    class Meta:
        ordering = ['niveau', 'date_creation']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'


class QuizOption(models.Model):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='options')
    texte = models.CharField(max_length=255)
    est_correcte = models.BooleanField(default=False)
    ordre = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.texte[:30]}... ({'✅' if self.est_correcte else '❌'})"
    
    class Meta:
        ordering = ['ordre']
        verbose_name = 'Option'
        verbose_name_plural = 'Options'


class QuizSession(models.Model):
    """Session de quiz pour un utilisateur"""
    user_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID utilisateur (pour plus tard)")
    score_total = models.PositiveIntegerField(default=0)
    questions_repondues = models.PositiveIntegerField(default=0)
    bonnes_reponses = models.PositiveIntegerField(default=0)
    niveau_actuel = models.CharField(max_length=20, choices=QuizQuestion.NIVEAU_CHOICES, default='facile')
    est_termine = models.BooleanField(default=False)
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Session {self.id} - {self.score_total} pts"
    
    class Meta:
        ordering = ['-date_debut']
        verbose_name = 'Session de quiz'
        verbose_name_plural = 'Sessions de quiz'


class QuizReponse(models.Model):
    """Réponse donnée à une question"""
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='reponses')
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    option_choisie = models.ForeignKey(QuizOption, on_delete=models.CASCADE, blank=True, null=True)
    est_correcte = models.BooleanField(default=False)
    temps_reponse = models.PositiveIntegerField(default=0, help_text="Temps de réponse en secondes")
    date_reponse = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q{self.question.id} - {'✅' if self.est_correcte else '❌'}"
    
    class Meta:
        verbose_name = 'Réponse'
        verbose_name_plural = 'Réponses'
        
        
from django.db import models
from django.contrib.auth.models import User

class PushToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, blank=True)  # 'android' ou 'ios'
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.token[:20]}..."
    
    

# === À AJOUTER TOUT EN BAS DU FICHIER ===
from django.db.models.signals import post_save
from django.dispatch import receiver
from .notif_services import send_push_notification_to_all_users

# Définition du signal DIRECTEMENT dans models.py
@receiver(post_save, sender='plantes.Article')  # ✅ Utiliser le nom complet
def notify_new_article_signal(sender, instance, created, **kwargs):
    """Déclenche une notification push quand un nouvel article est créé."""
    if created:
        print(f"📝 NOUVEL ARTICLE : {instance.titre}")
        
        send_push_notification_to_all_users(
            title=f"📰 Nouvel article : {instance.titre}",
            body=instance.extrait[:100] if instance.extrait else "Cliquez pour lire l'article",
            data={
                "screen": "ArticleDetail",
                "article_id": instance.id,
                "type": "blog"
            }
        )