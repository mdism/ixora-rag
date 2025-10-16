from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team, Role
from project_management.models import Customer

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """
    class Meta:
        model = Role
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for the Team model.
    """
    # Display the manager's username instead of their ID
    manager = serializers.StringRelatedField(read_only=True)
    customers = serializers.StringRelatedField(many=True , read_only=True)
    customer_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Customer.objects.all(),
        write_only=True,
        source="customers"
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'manager', 'members', 'customers', 'customer_ids']
        read_only_fields = ['members']


class LoginSerializer(serializers.ModelSerializer):
    """"
    To validate user.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model, including roles and teams.
    """
    # A nested serializer to represent the user's role.
    role = RoleSerializer(read_only=True)
    # A nested serializer to represent the teams the user is a member of.
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'is_active', 'date_joined',
            'is_superuser', 'role', 'teams'
        ]
        read_only_fields = ['date_joined', 'is_superuser']

class UserCreationSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new user, including password.
    """
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        # Create a new user with a hashed password
        user = User.objects.create_user(**validated_data)
        return user
