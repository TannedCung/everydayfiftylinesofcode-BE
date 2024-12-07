# urls.py

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.github.views import oauth2_login, oauth2_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # This includes all allauth URLs
    path('auth/', include('dj_rest_auth.urls')),
    path('api/', include('core.urls')),

    # OpenAPI schema generation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # ReDoc UI (optional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
