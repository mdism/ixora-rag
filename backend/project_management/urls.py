from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, TagViewSet, DocumentViewSet,
    UserCutomerAssignmentViewSet, ChatSessionViewSet, ChatMessageViewSet
)
from .views_rag import rag_query


router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename="customer")
router.register(r'tags', TagViewSet, basename="tag")
router.register(r'documents', DocumentViewSet, basename="document")
router.register(r'user-tag-assignments', UserCutomerAssignmentViewSet, basename="user-tag-assignment")
router.register(r'chat-sessions', ChatSessionViewSet, basename="chat-session")
router.register(r'chat-messages', ChatMessageViewSet, basename="chat-message")

urlpatterns = [
    path("", include(router.urls)),

    # RAG query endpoint
    path("rag/query/", rag_query, name="rag-query"),
]

