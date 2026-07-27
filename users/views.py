# users/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
import json
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .serializers import (
    UserSerializer, RegisterSerializer, 
    UserProfileSerializer, ReservationHistorySerializer
)
from .models import UserProfile
from reservations.models import Reservation

class RegisterView(generics.CreateAPIView):
    """Inscription d'un nouvel utilisateur"""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': '✅ Inscription réussie !'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        print("="*50)
        print("🔍 RECEPTION REQUETE LOGIN")
        print(f"📝 Data: {request.data}")
        print("="*50)
        
        username = request.data.get('username', '').strip() 
        password = request.data.get('password', '')
        
        print(f"🔍 Username reçu (nettoyé): '{username}'")
        print(f"🔍 Password reçu: '{password}'")
        
        if not username or not password:
            return Response(
                {'error': 'Nom d\'utilisateur et mot de passe requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 🔍 Vérifier si l'utilisateur existe avec le nom nettoyé
        user_exists = User.objects.filter(username=username).exists()
        print(f"🔍 Utilisateur existe dans DB: {user_exists}")
        
        # Authentifier avec le nom nettoyé
        user = authenticate(username=username, password=password)
        print(f"🔍 Authentification réussie: {user is not None}")
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': '✅ Connexion réussie !'
            })
        
        return Response(
            {'error': 'Identifiants invalides.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class ProfileView(generics.RetrieveUpdateAPIView):
    """Récupérer et modifier le profil de l'utilisateur connecté"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()
        
        # Mettre à jour le profil
        telephone = request.data.get('telephone')
        if telephone is not None:
            user.profile.telephone = telephone
            user.profile.save()
        
        return Response(UserSerializer(user).data)


class ReservationHistoryView(generics.ListAPIView):
    """Historique des réservations de l'utilisateur"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationHistorySerializer
    
    def get_queryset(self):
        # Récupérer les réservations avec l'email de l'utilisateur
        return Reservation.objects.filter(email=self.request.user.email).order_by('-date_creation')


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                try:
                    token.blacklist()
                except AttributeError:
                    # Fallback si blacklist n'est pas disponible
                    pass
            return Response({'message': 'Déconnexion réussie.'})
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )