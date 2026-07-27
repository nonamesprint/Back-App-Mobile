from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
    type_visite_label = serializers.SerializerMethodField()
    statut_label = serializers.SerializerMethodField()
    date_formatee = serializers.SerializerMethodField()
    heure_formatee = serializers.SerializerMethodField()
    
    class Meta:
        model = Reservation
        fields = '__all__'
        read_only_fields = ('reference', 'date_creation', 'date_modification')
    
    def get_type_visite_label(self, obj):
        return dict(Reservation.TYPE_VISITE_CHOICES).get(obj.type_visite, obj.type_visite)
    
    def get_statut_label(self, obj):
        return dict(Reservation.STATUT_CHOICES).get(obj.statut, obj.statut)
    
    def get_date_formatee(self, obj):
        return obj.date_visite.strftime('%d %B %Y')
    
    def get_heure_formatee(self, obj):
        return obj.heure_visite.strftime('%H:%M')