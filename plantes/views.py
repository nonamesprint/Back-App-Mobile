from rest_framework import viewsets
from .models import *
from .serializers import *
import qrcode
from io import BytesIO
from django.core.files import File
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework import viewsets, status
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import DetailView
from django.utils import timezone
import random


class PlantePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PlanteViewSet(viewsets.ModelViewSet):
    queryset = Plante.objects.all()
    serializer_class = PlanteSerializer
    pagination_class = PlantePagination
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        # Surcharge de la méthode de création pour générer le QR Code
        plante = serializer.save()
        self.generate_qr_code(plante)

    def perform_update(self, serializer):
        # Surcharge de la méthode de mise à jour
        plante = serializer.save()
        # On pourrait régénérer le QR code si l'URL change, ou le laisser tel quel
        # Ici, on le régénère toujours
        self.generate_qr_code(plante)

    def generate_qr_code(self, plante):
        # Générer l'URL unique pour la plante
        # Idéalement, l'URL serait celle de l'app mobile, ex: https://monapp.com/plante/{slug}
        # Pour le développement, nous allons utiliser une URL de test
        base_url = "http://192.168.43.171:8000/plante/"
        url = f"{base_url}{plante.slug}"
        plante.qr_code_url = url

        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Sauvegarder l'image dans le champ 'qr_code' du modèle
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        file_name = f"qr_{plante.slug}.png"
        plante.qr_code.save(file_name, File(buffer), save=False)  # save=False pour ne pas sauvegarder deux fois
        plante.save()

    @action(detail=True, methods=['get'])
    def qr_code(self, request, pk=None):
        """Endpoint pour récupérer l'image du QR Code d'une plante."""
        plante = self.get_object()
        if plante.qr_code:
            return Response({'qr_code_url': plante.qr_code.url})
        return Response({'error': 'QR Code non généré'}, status=404)
    


class PlanteDetailView(DetailView):
    model = Plante
    template_name = 'plantes/plante_detail.html'
    context_object_name = 'plante'
    
    

class CircuitViewSet(viewsets.ModelViewSet):
    queryset = Circuit.objects.filter(est_active=True)
    serializer_class = CircuitSerializer
    permission_classes = [AllowAny]
    pagination_class = PlantePagination  
    


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.filter(est_publie=True)
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    pagination_class = PlantePagination
    
    @action(detail=True, methods=['post'])
    def increment_vue(self, request, pk=None):
        article = self.get_object()
        
        # Récupérer l'IP du visiteur
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Vérifier si cette IP a déjà vu cet article
        vue_existante = ArticleVue.objects.filter(
            article=article,
            ip_address=ip
        ).exists()
        
        if not vue_existante:
            # Première vue : incrémenter le compteur
            article.vues += 1
            article.save()
            
            # Enregistrer la vue
            ArticleVue.objects.create(
                article=article,
                ip_address=ip,
                session_key=request.session.session_key
            )
            est_unique = True
        else:
            est_unique = False
        
        return Response({
            'vues': article.vues,
            'est_unique': est_unique,
            'message': 'Vue comptée' if est_unique else 'Déjà vu'
        })

class AbonneViewSet(viewsets.ModelViewSet):
    queryset = Abonne.objects.filter(est_actif=True)
    serializer_class = AbonneSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier si l'email existe déjà
        email = request.data.get('email')
        if Abonne.objects.filter(email=email, est_actif=True).exists():
            return Response(
                {'error': 'Cet email est déjà abonné.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        self.perform_create(serializer)
        
        # Envoyer un email de confirmation (optionnel)
        try:
            send_mail(
                'Bienvenue au Jardin Botanique !',
                f"Bonjour {request.data.get('nom', 'visiteur')},\n\nMerci de vous être abonné au blog du Jardin Botanique. Vous recevrez nos prochains articles directement dans votre boîte mail.\n\nL'équipe du Jardin Botanique",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
        except:
            pass
        
        return Response(
            {'message': 'Abonnement réussi ! Bienvenue dans la communauté du Jardin Botanique.'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['post'])
    def unsubscribe(self, request):
        email = request.data.get('email')
        try:
            abonne = Abonne.objects.get(email=email)
            abonne.est_actif = False
            abonne.save()
            return Response({'message': 'Désabonnement réussi.'})
        except Abonne.DoesNotExist:
            return Response(
                {'error': 'Cet email n\'est pas dans notre liste.'},
                status=status.HTTP_404_NOT_FOUND
            )
            
            
class ArticleDetailView(DetailView):
    model = Article
    template_name = 'plantes/article_detail.html'
    context_object_name = 'article'
    
    



class QuizQuestionViewSet(viewsets.ModelViewSet):
    """Vue pour les questions du quiz"""
    queryset = QuizQuestion.objects.filter(est_active=True)
    serializer_class = QuizQuestionSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        """Récupérer une question aléatoire par niveau"""
        niveau = request.query_params.get('niveau', 'facile')
        exclude_ids = request.query_params.get('exclude', '')
        
        queryset = QuizQuestion.objects.filter(est_active=True, niveau=niveau)
        
        if exclude_ids:
            ids = [int(id) for id in exclude_ids.split(',') if id.isdigit()]
            queryset = queryset.exclude(id__in=ids)
        
        if not queryset.exists():
            return Response(
                {'error': 'Plus de questions disponibles pour ce niveau'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        question = random.choice(queryset)
        serializer = QuizQuestionSerializer(question)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reponse(self, request, pk=None):
        """Vérifier une réponse"""
        question = self.get_object()
        option_id = request.query_params.get('option_id')
        
        try:
            option = QuizOption.objects.get(id=option_id, question=question)
        except QuizOption.DoesNotExist:
            return Response(
                {'error': 'Option invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'est_correcte': option.est_correcte,
            'bonne_reponse_id': question.options.filter(est_correcte=True).first().id if option.est_correcte else None,
        })


class QuizSessionViewSet(viewsets.ModelViewSet):
    """Vue pour les sessions de quiz"""
    queryset = QuizSession.objects.all()
    serializer_class = QuizSessionSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle session de quiz"""
        niveau = request.data.get('niveau', 'facile')
        user_id = request.data.get('user_id', None)
        
        session = QuizSession.objects.create(
            user_id=user_id,
            niveau_actuel=niveau,
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def repondre(self, request, pk=None):
        """Répondre à une question"""
        session = self.get_object()
        
        if session.est_termine:
            return Response(
                {'error': 'Cette session est déjà terminée'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        question_id = request.data.get('question_id')
        option_id = request.data.get('option_id')
        temps_reponse = request.data.get('temps_reponse', 0)
        
        try:
            question = QuizQuestion.objects.get(id=question_id)
        except QuizQuestion.DoesNotExist:
            return Response(
                {'error': 'Question invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            option = QuizOption.objects.get(id=option_id, question=question)
        except QuizOption.DoesNotExist:
            return Response(
                {'error': 'Option invalide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        est_correcte = option.est_correcte
        
        # Créer la réponse
        reponse = QuizReponse.objects.create(
            session=session,
            question=question,
            option_choisie=option,
            est_correcte=est_correcte,
            temps_reponse=temps_reponse,
        )
        
        # Mettre à jour la session
        session.questions_repondues += 1
        if est_correcte:
            session.bonnes_reponses += 1
            session.score_total += question.points
        session.save()
        
        return Response({
            'est_correcte': est_correcte,
            'points_gagnes': question.points if est_correcte else 0,
            'score_total': session.score_total,
            'questions_repondues': session.questions_repondues,
            'bonnes_reponses': session.bonnes_reponses,
            'pourcentage': round((session.bonnes_reponses / session.questions_repondues) * 100),
        })
    
    @action(detail=True, methods=['post'])
    def terminer(self, request, pk=None):
        """Terminer une session de quiz"""
        session = self.get_object()
        session.est_termine = True
        session.date_fin = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resultats(self, request, pk=None):
        """Récupérer les résultats d'une session"""
        session = self.get_object()
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import PushToken

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_push_token(request):
    """Enregistre le token de notification push de l'utilisateur."""
    token = request.data.get('token')
    platform = request.data.get('platform', 'android')

    if not token:
        return Response(
            {'error': 'Token requis'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Mettre à jour ou créer le token
    push_token, created = PushToken.objects.update_or_create(
        user=request.user,
        token=token,
        defaults={
            'platform': platform,
            'is_active': True,
        }
    )

    return Response({
        'status': 'created' if created else 'updated',
        'message': 'Token enregistré avec succès'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_push_token(request):
    """Désactive le token de notification push de l'utilisateur."""
    token = request.data.get('token')

    if not token:
        return Response(
            {'error': 'Token requis'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        push_token = PushToken.objects.get(user=request.user, token=token)
        push_token.is_active = False
        push_token.save()
        return Response({'status': 'unregistered'})
    except PushToken.DoesNotExist:
        return Response(
            {'error': 'Token non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )