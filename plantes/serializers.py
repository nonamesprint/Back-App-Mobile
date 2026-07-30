from rest_framework import serializers
from .models import *
from django.conf import settings

class PlanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plante
        # fields = '__all__'  # On peut afficher tous les champs pour le moment
        # Ou une liste spécifique :
        fields = ['id', 'nom_scientifique', 'nom_commun_fr', 'description', 'image_principale', 'qr_code_url',"famille_botanique","zone_geographique","anecdote"]
    
    # def get_image_principale(self, obj):
    #     if obj.image_principale:
    #         # Construire l'URL complète avec l'IP
    #         return f"http://192.168.43.171:8000{obj.image_principale.url}"
    #     return None
    def get_image_principale(self, obj):
      """Retourne l'URL complète de l'image principale"""
      if obj.image_principale:
        # Utiliser les paramètres de l'environnement
        base_url = settings.BASE_URL.rstrip('/')
        image_url = obj.image_principale.url
        return f"{base_url}{image_url}"
      return None


class CircuitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Circuit
        fields = '__all__'
        



class ArticleSerializer(serializers.ModelSerializer):
    date_formatee = serializers.SerializerMethodField()
    categorie_label = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = '__all__'
    
    def get_date_formatee(self, obj):
        return obj.date_publication.strftime('%d %B %Y')
    
    def get_categorie_label(self, obj):
        return dict(Article._meta.get_field('categorie').choices).get(obj.categorie, obj.categorie)
    
    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',')]
        return []

class AbonneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Abonne
        fields = ['id', 'email', 'nom', 'est_actif', 'date_abonnement']
        




class QuizOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizOption
        fields = ['id', 'texte', 'ordre', 'est_correcte']


class QuizQuestionSerializer(serializers.ModelSerializer):
    options = QuizOptionSerializer(many=True, read_only=True)
    niveau_label = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'niveau', 'niveau_label', 'points', 'temps_estime', 'options']
    
    def get_niveau_label(self, obj):
        return dict(QuizQuestion.NIVEAU_CHOICES).get(obj.niveau, obj.niveau)


class QuizQuestionReponseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour une question avec la bonne réponse (pour le corrigé)"""
    options = QuizOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'options', 'points']


class QuizReponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizReponse
        fields = ['id', 'question', 'option_choisie', 'est_correcte', 'temps_reponse', 'date_reponse']


class QuizSessionSerializer(serializers.ModelSerializer):
    reponses = QuizReponseSerializer(many=True, read_only=True)
    niveau_label = serializers.SerializerMethodField()
    pourcentage_reussite = serializers.SerializerMethodField()
    
    class Meta:
        model = QuizSession
        fields = ['id', 'score_total', 'questions_repondues', 'bonnes_reponses', 
                  'niveau_actuel', 'niveau_label', 'est_termine', 'date_debut', 
                  'date_fin', 'pourcentage_reussite', 'reponses']
    
    def get_niveau_label(self, obj):
        return dict(QuizQuestion.NIVEAU_CHOICES).get(obj.niveau_actuel, obj.niveau_actuel)
    
    def get_pourcentage_reussite(self, obj):
        if obj.questions_repondues > 0:
            return round((obj.bonnes_reponses / obj.questions_repondues) * 100)
        return 0