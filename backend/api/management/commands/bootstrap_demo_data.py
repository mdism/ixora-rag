from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Team, Role
from project_management.models import Customer, Tag, Document

User = get_user_model()


class Command(BaseCommand):
    help = "Bootstrap demo users, teams, roles, projects, and tags"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Bootstrapping demo data..."))

        # --- Roles ---
        roles = ["Admin", "Manager", "Developer", "Viewer"]
        role_objs = {}
        for role in roles:
            obj, _ = Role.objects.get_or_create(name=role)
            role_objs[role] = obj
        self.stdout.write(self.style.SUCCESS("✅ Roles created"))

        # --- Teams ---
        teams = ["Team Alpha", "Team Beta", "Team Gama"]
        team_objs = {}
        for team in teams:
            obj, _ = Team.objects.get_or_create(name=team)
            team_objs[team] = obj
        self.stdout.write(self.style.SUCCESS("✅ Teams created"))

        # --- Users ---
        users = [
            {"username": "admin", "email": "admin@example.com", "role": "Admin", "team": "Team Alpha", "password":"Info@1234", 'is_super_user': False},
            {"username": "manager1", "email": "manager1@example.com", "role": "Manager", "team": "Team Alpha",  "password":"Info@1234", 'is_super_user': False},
            {"username": "dev1", "email": "dev1@example.com", "role": "Developer", "team": "Team Alpha",  "password":"Info@1234", 'is_super_user': False},
            {"username": "dev2", "email": "dev2@example.com", "role": "Developer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': False},
            {"username": "viewer1", "email": "viewer1@example.com", "role": "Viewer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': False},
            {"username": "mdism", "email": "viewer1@example.com", "role": "Viewer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': True},
            {"username": "parvez", "email": "parvez@ixoratechnologies.com", "role": "Viewer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': True},
            {"username": "preeti", "email": "preeti@ixoratechnologies.com", "role": "Viewer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': True},
            {"username": "shafee", "email": "shafee@ixoratechnologies.com", "role": "Viewer", "team": "Team Beta",  "password":"Info@1234", 'is_super_user': True},
        ]

        for u in users:
            user, created = User.objects.get_or_create(
                username=u["username"],
                defaults={"email": u["email"]}
            )
            if created:
                user.set_password(u['password'])
                user.save()

            # Assign role
            user.role = role_objs[u["role"]]
            user.save()

            # Assign team
            user.teams.add(team_objs[u["team"]])
        
        for u in users:
            user_by_id = User.objects.get(username=u['username'])
            if u['is_super_user'] and user_by_id:
                user_by_id.is_superuser = True
                user_by_id.is_staff = True
                user_by_id.save()
                    


        self.stdout.write(self.style.SUCCESS("✅ Users created and assigned roles/teams"))

        # --- Customers / Projects ---
        customers = ["CustomerA", "CustomerB"]
        for cname in customers:
            cust, created = Customer.objects.get_or_create(name=cname)
            if created:
                cust.save()
    
        self.stdout.write(self.style.SUCCESS("✅ Customers Tags created"))

        Tags = ['Infra', "Network", "Cloud"]
        for tag in Tags:
            tag, created = Tag.objects.get_or_create(name=tag)
            if created:
                tag.save()
        
        self.stdout.write(self.style.SUCCESS("✅ Tags created"))
        

        # --- User ↔ Tag assignment (basic example) ---
        # Example: create a manager user
        # manager = User.objects.create_user(username="manager1", email="m1@example.com", password="test123")
        # role_manager = Role.objects.get_or_create(name="Manager")[0]
        # manager.role = role_manager
        # manager.save()

        # # Create team and set manager directly (bypassing perform_create)
        # team_alpha = Team.objects.create(name="Alpha Team", description="Bootstrap team", manager=manager)

        # Add members
        # member = User.objects.create_user(username="dev1", email="d1@example.com", password="test123")
        # team_alpha.members.add(member)

        # # Create customer + tag
        # cust = Customer.objects.create(name="ACME Corp")
        # tag = Tag.objects.create(name="Networking", customer=cust)

        # self.stdout.write(self.style.SUCCESS("✅ User-tag assignments created"))
        self.stdout.write(self.style.SUCCESS("🎉 Bootstrap complete"))