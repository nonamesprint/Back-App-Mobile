# users/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile
from reservations.models import Reservation

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['telephone',  'date_creation']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    telephone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'telephone']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        telephone = validated_data.pop('telephone', '')
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Mettre à jour le profil avec le téléphone
        if telephone:
            user.profile.telephone = telephone
            user.profile.save()
        
        return user


class ReservationHistorySerializer(serializers.ModelSerializer):
    type_visite_label = serializers.SerializerMethodField()
    statut_label = serializers.SerializerMethodField()
    date_formatee = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = ['reference', 'nom', 'type_visite', 'type_visite_label', 
                  'date_visite', 'date_formatee', 'statut', 'statut_label']
    
    def get_type_visite_label(self, obj):
        return dict(Reservation.TYPE_VISITE_CHOICES).get(obj.type_visite, obj.type_visite)
    
    def get_statut_label(self, obj):
        return dict(Reservation.STATUT_CHOICES).get(obj.statut, obj.statut)
    
    def get_date_formatee(self, obj):
        return obj.date_visite.strftime('%d/%m/%Y')