# # Jardin/admin.py
# from django.contrib import admin
# from rest_framework_simplejwt.token_blacklist.models import (
#     BlacklistedToken,
#     OutstandingToken
# )

# # ✅ Cacher les modèles de tokens de l'admin
# admin.site.unregister(BlacklistedToken)
# admin.site.unregister(OutstandingToken)

# Jardin/admin.py
from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken
)

print("🔍 Chargement de Jardin/admin.py")

try:
    admin.site.unregister(BlacklistedToken)
    print("✅ BlacklistedToken désenregistré")
except Exception as e:
    print(f"⚠️ Erreur désenregistrement BlacklistedToken: {e}")

try:
    admin.site.unregister(OutstandingToken)
    print("✅ OutstandingToken désenregistré")
except Exception as e:
    print(f"⚠️ Erreur désenregistrement OutstandingToken: {e}")
