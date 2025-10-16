

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from api import views
from django.conf.urls import static

urlpatterns = [
    path("", views.Server_Test.as_view(), name='test'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path("api/", include("project_management.urls")),


    # Creating API Documentation 
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
