from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from plantes.views import *

from django.http import JsonResponse
from django.shortcuts import redirect

def home_view(request):
    return JsonResponse({
        "message": "Bienvenue sur l'API du Jardin Botanique !",
        "endpoints": {
            "admin": "/admin",
            "api_plantes": "/api/plantes/",
            
        }
    })


urlpatterns = [
    path('', home_view),  
    path("admin/", admin.site.urls),
    path('api/', include('plantes.urls')),
    path('api/', include('reservations.urls')),
     path('api/auth/', include('users.urls')),
    path('plante/<slug:slug>/', PlanteDetailView.as_view(), name='plante_detail'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),

]

# Servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)