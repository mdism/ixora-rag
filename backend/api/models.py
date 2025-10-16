from django.db import models
from django.contrib.auth.models import User



class Role(models.Model):
    """
    Represents user roles (e.g., Admin, Manager, User).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    """
    Represents a team with a manager and members.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    # Manager is a ForeignKey to the User model
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_teams'
    )
    customers = models.ManyToManyField(
        "project_management.Customer",     
        related_name="teams",
        blank=True
    )    
    # Members are a ManyToMany relationship to the User model
    members = models.ManyToManyField(
        User,
        related_name='teams',
        blank=True
    )

    def __str__(self):
        return self.name
