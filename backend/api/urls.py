from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (TeamViewSet, 
                    RoleViewSet, UserViewSet, 
                    RegisterView, 
                    LoginView, 
                    Server_Test, get_user_profile)


router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('me/', get_user_profile, name='user-profile'),
    path('welcome/', Server_Test.as_view(), name='welcome'),
    path('check/', Server_Test.as_view(), name='check'),
]

