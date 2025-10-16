from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rag_pipeline.pipline import index_document
from .models import (Customer, Tag, Document, UserCustomerAssignment, ChatSession, ChatMessage)
from .serializers import (CustomerSerializer, TagSerializer, DocumentSerializer, UserCustomersAssignmentSerializer, ChatSessionSerializer, ChatMessageSerializer)
from .permissions import IsAdminOrReadOnly, CanUploadDocument, IsCustomerMember


class UserCustomerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = UserCustomerAssignment.objects.all()
    serializer_class = UserCustomersAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly] # Admins manage assignments

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return UserCustomerAssignment.objects.all()
        else:
            # Regular users might only see their own assignments
            # Or, if they are managers for a customer or team, they might see others
            # Adjust based on your specific admin/manager role definitions
            # For now, just showing own assignments or assignments for customers accessible via teams
            # This might be complex depending on management scope.
            # Example: return UserCustomerAssignment.objects.filter(user=user)
            # Or allow if user is a manager for a customer via direct assignment or team membership
            # For simplicity in this context, let's keep it as admin-only or user's own.
            # Access control for *viewing* assignments should be carefully considered based on business rules.
            return UserCustomerAssignment.objects.filter(user=user) # Example: users see their own assignments

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=["get"], url_path="documents")
    def documents(self, request, pk=None):
        """Get all documents for this customer (filtered by user permissions)."""
        customer = self.get_object()
        user = request.user

        if user.is_superuser:
            docs = Document.objects.filter(customer=customer)
        else:
            docs = Document.objects.filter(
                customer=customer,
                tag__usercustomerassignment__user=user
            ).distinct()

        serializer = DocumentSerializer(docs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="tags")
    def tags(self, request, pk=None):
        """Get all tags for this customer."""
        customer = self.get_object()
        tags = Tag.objects.filter(documents__customer=customer).distinct()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=True, methods=["get"], url_path="documents")
    def documents(self, request, pk=None):
        """Get all documents linked to this tag (filtered by user)."""
        tag = self.get_object()
        user = request.user

        if user.is_superuser:
            docs = Document.objects.filter(tag=tag)
        else:
            docs = Document.objects.filter(tag=tag, tag__usercustomerassignment__user=user).distinct()

        serializer = DocumentSerializer(docs, many=True, context={"request": request})
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated & CanUploadDocument]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Document.objects.all()
        return Document.objects.filter(
            customer__usercustomerassignment__user=user,
            tag__usercustomerassignment__user=user
        ).distinct()

    def perform_create(self, serializer):
        # Save document first
        document = serializer.save(uploaded_by=self.request.user)

        # Call RAG ingestion (async would be better, but start with sync)
        try:
            index_document(document.id, document.file.path, customer_id=document.customer_id, tag_id = document.tag_id)
        except Exception as e:
            # Optional: log error, don't block upload if ingestion fails
            print(f"Error ingesting document {document.id}: {e}")

    @action(detail=False, methods=["get"], url_path="my-documents")
    def my_documents(self, request):
        """Get all documents assigned to the logged-in user across customers & tags."""
        user = request.user
        if user.is_superuser:
            docs = Document.objects.all()
        else:
            docs = Document.objects.filter(
                customer__usercustomerassignment__user=user,
                tag__usercustomerassignment__user=user
            ).distinct()

        serializer = DocumentSerializer(docs, many=True, context={"request": request})
        return Response(serializer.data)



class UserCutomerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = UserCustomerAssignment.objects.all()
    serializer_class = UserCustomersAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


    @action(detail=False, methods=["get"], url_path="my-customers")
    def get_queryset(self):
        user = self.request.user
        # Example: Only show assignments for the requesting user
        # return UserCustomerAssignment.objects.filter(user=user)
        # Or show all if admin, filter if regular user, etc.
        return super().get_queryset()


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerMember] # Use updated permission

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ChatSession.objects.all()
        # Filter by sessions where the user has access to the customer
        # This can be via direct assignment OR team membership
        return ChatSession.objects.filter(
            usercustomerassignment__user=user # Link through direct assignment
        ).distinct() | ChatSession.objects.filter( # OR
            customer__teams__members=user # Link through team membership -> customer
        ).distinct() # Combine and ensure unique sessions

    @action(detail=False, methods=["get"], url_path="my-sessions")
    def my_sessions(self, request):
        """Get all chat sessions the user has access to (i.e., their own)."""
        user = request.user

        if user.is_superuser:
            sessions = ChatSession.objects.all()
        else:
            sessions = ChatSession.objects.filter(user=user)

        serializer = ChatSessionSerializer(sessions, many=True)
        return Response(serializer.data)


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerMember] # Use updated permission

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ChatMessage.objects.all()
        # Filter by messages in sessions where the user has access to the customer
        # This can be via direct assignment OR team membership
        return ChatMessage.objects.filter(
            session__usercustomerassignment__user=user # Link through session -> direct assignment
        ).distinct() | ChatMessage.objects.filter( # OR
            session__customer__teams__members=user # Link through session -> customer -> team membership
        ).distinct() # Combine and ensure unique messages


