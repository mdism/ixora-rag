from rest_framework import serializers
from .models import Customer, Tag, Document, UserCustomerAssignment, ChatMessage, ChatSession
from api.models import Team
from django.conf import settings
from api.models import Role
from django.contrib.auth.models import User



class CustomerSerializer(serializers.ModelSerializer):
    teams = serializers.StringRelatedField(many=True, read_only=True)
    contact = serializers.EmailField()
    teams_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Team.objects.all(),
        write_only=True,
        source="teams"
    )
    
    class Meta:
        model = Customer
        fields = ["id", "name", "contact", "description", "created_at", 'updated_at','teams', 'teams_ids']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "description"]

class DocumentSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    tag = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all())
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "file_name",
            "file",
            "uploaded_by",
            "uploaded_at",
            "customer",
            "tag"
        ]

    def create(self, validated_data):
        validated_data["uploaded_by"] = self.context["request"].user
        return super().create(validated_data)

class UserCustomersAssignmentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all())
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all())

    class Meta:
        model = UserCustomerAssignment
        fields = ["id", "user", "customer", "role"]


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(read_only=True)
    provider = serializers.CharField(read_only=True)
    customer = serializers.StringRelatedField(read_only=True) # Or PrimaryKeyRelatedField(write_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "sender", "message", "created_at", "provider", "customer"] # Include new fields
        # Exclude session from direct write if it's set by the view logic
        # read_only_fields = ('session',) # If session is set internally in the view

    # Optional: Override to_representation for more detailed customer/provider info
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['customer_details'] = {'id': instance.customer.id, 'name': instance.customer.name}
        # Add provider details if needed
        data.pop('customer') # Remove simple name if using nested details
        return data

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    initial_customer = serializers.StringRelatedField(read_only=True) # Or PrimaryKeyRelatedField if needed for input
    user = serializers.StringRelatedField(read_only=True) # Or PrimaryKeyRelatedField if needed for input

    class Meta:
        model = ChatSession
        fields = ["id", "user", "initial_customer", "started_at", "messages"]
        read_only_fields = ('user', 'initial_customer')
