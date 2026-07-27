from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from . import views

router = DefaultRouter()
router.register(r'plantes', PlanteViewSet, basename='plante')
router.register(r'circuits', CircuitViewSet, basename='circuit') 
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'abonnes', AbonneViewSet, basename='abonne') 
router.register(r'quiz-questions', QuizQuestionViewSet, basename='quiz-question')
router.register(r'quiz-sessions', QuizSessionViewSet, basename='quiz-session')

urlpatterns = [
    path('register-token/', views.register_push_token, name='register_push_token'),
    path('unregister-token/', views.unregister_push_token, name='unregister_push_token'),
    path('', include(router.urls)),
]