from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Team, Role
from project_management.models import Customer
from .serializers import (
    TeamSerializer, RoleSerializer, UserSerializer, UserCreationSerializer,
    LoginSerializer
)


class RegisterView(APIView):
    """User Registration API view, 

    Args:
        JSON {
            (username): Username
            }

    Returns:
        _type_: _description_
    """
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user=user)
                return Response({
                    'message': 'user registered successfully!',
                    'user': serializer.data,
                    'refresh-token':str(refresh),
                    'access-token':str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':"error while processing the request, please try again!"}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

from drf_spectacular.utils import extend_schema

@extend_schema(request=LoginSerializer)
class LoginView(APIView):
    permission_classes =[AllowAny]
    # serializer_class = LoginSerializer
    serializer_class = LoginSerializer
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': "login successfully!",
                    'refresh-token': str(refresh),
                    'access-token': str(refresh.access_token)
                }, status=status.HTTP_202_ACCEPTED)
            
            return Response({'error': "invalid credentials!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':"error while processing the request, please try again!"}, status=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

            
        
@extend_schema(responses={200: {'description': 'A success message indicating the user is authenticated.'}})
class Server_Test(APIView):
    """
    An after login endpoint that requires a valid JWT token. and tells the server status too.
    """    
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not request.user:
            context = {
                'message': f"Welcome {request.user.username}, this is a protected route",
                'user_id': request.user.id,
                'version': settings.VERSION,
                'setup': "DEV" if settings.DEBUG == True else "PROD",
                'database': "DEV" if settings.ENABLE_DATABASE_TYPE == True else "PROD"
            }
        else:
            context = {
                'message': f'Server is running!',
                'version': settings.VERSION,
                'setup': "DEV" if settings.DEBUG == True else "PROD",
                'database': "DEV" if settings.ENABLE_DATABASE_TYPE == True else "PROD"
                
            }
            
        
        return Response(context)

class CustomIsAdminUser(IsAdminUser):
    """
    Custom permission to check if the user is an admin.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class TeamManagerPermission(IsAuthenticated):
    """
    Custom permission to allow a user to manage their own team.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.manager or request.user.is_superuser

class RoleViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing roles.
    Only admin users can access this view.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [CustomIsAdminUser]

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing teams.
    Admins can do anything. Managers can only manage their own team.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Set permissions for each action.
        """
        if self.action in ['create', 'list']:
            self.permission_classes = [CustomIsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [TeamManagerPermission]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        # Automatically set the manager of the new team to the requesting user.
        serializer.save(manager=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[TeamManagerPermission])
    def add_user(self, request, pk=None):
        """
        Custom action to add a user to a team.
        """
        team = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        team.members.add(user)
        return Response({'status': 'user added to team'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[TeamManagerPermission])
    def remove_user(self, request, pk=None):
        """
        Custom action to remove a user from a team.
        """
        team = self.get_object()
        user_id = request.data.get('user_id')
        user = get_object_or_404(User, id=user_id)
        team.members.remove(user)
        return Response({'status': 'user removed from team'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[TeamManagerPermission])
    def add_customer(self, request, pk=None):
        """
        action to add a customer to a team./ assign team a customer. 
        """
        team = self.get_object()
        customer_id = request.data.get('customer_id')
        customer = get_object_or_404(Customer, id=customer_id)
        team.customers.add(customer)
        return Response({'status':"customer is added", "customer_id": customer_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[TeamManagerPermission])
    def remove_customer(self, request, pk=None):
        """
        Action to remove the customer form a teams assignment
        """
        team = self.get_object
        customer_id = request.data.get('customer_id')
        customer = get_object_or_404(Customer, customer_id)
        team.customers.remove(customer)
        return Response({'status':f"customer {customer_id} - {customer.name} is remove form team {team.name}"}, status=status.HTTP_200_OK)

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing users.
    Admins can do everything. Regular users can only see and update their own profile.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """
        Use a different serializer for user creation.
        """
        if self.action == 'create':
            return UserCreationSerializer
        return UserSerializer

    def get_permissions(self):
        """
        Set permissions based on the action.
        """
        if self.action in ['list', 'create', 'destroy']:
            self.permission_classes = [CustomIsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_object(self):
        """
        Allow users to get their own profile using 'me'.
        """
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()
    
    def perform_create(self, serializer):
        # By default, a new user's role is set to 'user'
        user = serializer.save(is_active=False)
        default_role, created = Role.objects.get_or_create(name='user')
        user.role = default_role
        user.save()

    @action(detail=True, methods=['post'], permission_classes=[CustomIsAdminUser])
    def set_role(self, request, pk=None):
        """
        Custom action to set a user's role.
        """
        user = self.get_object()
        role_id = request.data.get('role_id')
        role = get_object_or_404(Role, id=role_id)
        user.role = role
        user.save()
        return Response({'status': 'role updated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[CustomIsAdminUser])
    def deactivate(self, request, pk=None):
        """
        Custom action to deactivate a user.
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """
        Custom action to allow a user to change their password.
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            return Response({'status': 'password updated'}, status=status.HTTP_200_OK)
        return Response({'error': 'new_password is required'}, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.decorators import api_view, permission_classes
from project_management.models import UserCustomerAssignment, Document
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    GET endpoint to retrieve the profile of the currently authenticated user,
    including their teams, customers (via team or direct assignment), roles, and documents.
    """
    user = request.user
    this_user = get_object_or_404(User, id=user.id )

    # --- User Info ---
    user_data = {
        "id": this_user.id,
        "username": this_user.username,
        "first_name": this_user.first_name,
        "last_name": this_user.last_name,
        "email": this_user.email,
        'is_superadmin': this_user.is_superuser,
        'is_staff': this_user.is_staff,
        # Add other user fields as needed
    }

    # --- Teams (User is member or manager) ---
    teams_user_is_member_of = Team.objects.filter(members=user)
    teams_user_manages = Team.objects.filter(manager=user)
    all_teams = (teams_user_is_member_of | teams_user_manages).distinct()

    teams_data = []
    for team in all_teams:
        teams_data.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "manager": {"id": team.manager.id, "username": team.manager.username} if team.manager else None,
            # Optionally include customers assigned to this team
            "customers": [{"id": c.id, "name": c.name} for c in team.customers.all()]
        })

    # --- Roles (User has via direct assignment or potentially via team role - though model is direct currently) ---
    # Get direct assignments
    direct_assignments = UserCustomerAssignment.objects.filter(user=user).select_related('customer', 'role')
    roles_data = []
    for assignment in direct_assignments:
        roles_data.append({
            "id": assignment.id,
            "customer": {"id": assignment.customer.id, "name": assignment.customer.name},
            "role": {"id": assignment.role.id, "name": assignment.role.name},
            "assignment_type": "direct" # Indicate the source
        })

    # Get assignments via team membership
    # Note: Your current UserCustomerAssignment model links user->customer->role directly.
    # If teams had roles *per customer*, you'd need a different model (e.g., TeamCustomerAssignment).
    # For now, we'll just list customers associated with teams the user belongs to.
    # You might want to add a field like 'default_role_for_team' to Team or Customer if needed.
    teams_customers = Customer.objects.filter(teams__members=user).distinct()
    for customer in teams_customers:
        # Find the team(s) this customer is linked to for the user
        user_teams_for_customer = Team.objects.filter(members=user, customers=customer)
        for team in user_teams_for_customer:
            roles_data.append({
                "id": f"team_{team.id}_customer_{customer.id}", # Generate a unique ID for this relationship
                "customer": {"id": customer.id, "name": customer.name},
                "role": {"id": None, "name": f"Member of Team '{team.name}'"}, # Indicate role via team membership
                "assignment_type": "via_team", # Indicate the source
                "team": {"id": team.id, "name": team.name} # Include team info
            })

    # --- Customers (Assigned via team or direct assignment) ---
    # Combine customers from direct assignments and team assignments
    direct_customer_ids = direct_assignments.values_list('customer_id', flat=True)
    teams_customer_ids = teams_customers.values_list('id', flat=True)
    all_customer_ids = set(list(direct_customer_ids) + list(teams_customer_ids)) # Use set to avoid duplicates

    customers_data = []
    for customer_id in all_customer_ids:
        customer = Customer.objects.get(id=customer_id)
        customers_data.append({
            "id": customer.id,
            "name": customer.name,
            "contact": customer.contact,
            "description": customer.description,
            # Optionally, indicate how the user is linked (directly or via which team(s))
            # This requires checking both direct_assignments and teams_customers again
        })

    # --- Documents (User has access to via customer/team assignment) ---
    # Get customer IDs the user has access to (from above)
    # Get documents associated with those customers
    # Note: This might also depend on tags if tags are used for further access control within a customer.
    # For now, assuming access to all documents of assigned customers.
    documents_user_can_access = Document.objects.filter(
        customer_id__in=all_customer_ids
    ).select_related('customer', 'tag', 'uploaded_by') # Optimize queries

    documents_data = []
    for doc in documents_user_can_access:
        documents_data.append({
            "id": doc.id,
            "file_name": doc.file_name,
            "customer": {"id": doc.customer.id, "name": doc.customer.name},
            "tag": {"id": doc.tag.id, "name": doc.tag.name},
            "uploaded_by": {"id": doc.uploaded_by.id, "username": doc.uploaded_by.username} if doc.uploaded_by else None,
            "uploaded_at": doc.uploaded_at,
            # Add other relevant document fields (e.g., file size, type if needed)
        })

    # --- Compile Response ---
    profile_data = {
        "user": user_data,
        "teams": teams_data,
        "roles": roles_data,
        "customers": customers_data,
        "documents": documents_data,
    }

    return Response(profile_data)