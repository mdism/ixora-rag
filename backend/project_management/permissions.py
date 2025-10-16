# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import UserCustomerAssignment, Document
from api.models import Team


class IsAdminOrReadOnly(BasePermission):
    """
    Allows full access to admins, read-only for others.
    """
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS or
            (request.user and request.user.is_superuser)
        )


class IsCustomerMember(BasePermission):
    """
    Grants access if the user:
    1. Is assigned directly to the customer via UserCustomerAssignment, OR
    2. Is a member of a team assigned to the customer (Team.customers).
    Admins bypass.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        customer = None

        # Handle object types
        if isinstance(obj, Document):  # Accessing a document
            customer = obj.customer
        elif hasattr(obj, "customer"):  # e.g., ChatSession, UserCustomerAssignment
            customer = obj.customer
        elif hasattr(obj, "session"):  # ChatMessage
            customer = obj.session.customer # Check customer of the parent session
        elif isinstance(obj, Team): # Accessing a team object itself (e.g., list teams assigned to a customer)
            # This permission might not be suitable for accessing Team objects directly
            # depending on your specific needs for Team CRUD.
            # If accessing a Team requires checking if user is member/manager of *that* team:
            return obj in Team.objects.filter(members=request.user) or obj.manager == request.user
            # Or if accessing a Team requires checking if user has access to *any* customer of that team:
            # return Team.objects.filter(id=obj.id, members=request.user, customers__isnull=False).exists()
            # Adjust based on Team-level access requirements.

        if not customer:
            return False

        # Check if user is assigned to the customer directly
        direct_assignment_exists = UserCustomerAssignment.objects.filter(
            user=request.user,
            customer=customer
        ).exists()

        # Check if user is a member of a team assigned to the customer
        team_assignment_exists = Team.objects.filter(
            members=request.user,
            customers=customer
        ).exists()

        # User has access if either condition is true
        return direct_assignment_exists or team_assignment_exists


class CanUploadDocument(BasePermission):
    """
    Only customer managers (via UserCustomerAssignment role) or team managers
    (via Team.manager) for the specific customer, or admin can upload documents.
    """
    def has_permission(self, request, view):
        if request.method not in ["POST"]:
            return True  # only enforce on create/upload

        if request.user.is_superuser:
            return True

        customer_id = request.data.get("customer")

        if not customer_id:
            return False

        # Check if user is a manager for the specified customer via UserCustomerAssignment
        user_direct_manager = UserCustomerAssignment.objects.filter(
            user=request.user,
            customer_id=customer_id,
            role__name__iexact="manager" # Assuming role name determines permissions
        ).exists()

        # Check if user is the manager of a team assigned to the specified customer
        user_team_manager = Team.objects.filter(
            manager=request.user,
            customers=customer_id
        ).exists()

        # User can upload if they are a direct manager OR a team manager for that customer
        return user_direct_manager or user_team_manager

    # Note: Consider adding has_object_permission if you need to restrict
    # editing/deleting documents based on role (direct or team-based manager).