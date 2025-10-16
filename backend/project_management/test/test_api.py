import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from project_management.models import Customer, Project, UserProject

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username="admin", password="adminpass")


@pytest.fixture
def auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

# @pytest.fixture
# def create_file():

def test_customer_crud(auth_client):
    # CREATE
    resp = auth_client.post("/api/customers/", {"name": "Test", "description": "Desc"})
    assert resp.status_code == 201
    customer_id = resp.data["id"]

    # READ
    resp = auth_client.get(f"/api/customers/{customer_id}/")
    assert resp.status_code == 200

    # UPDATE
    resp = auth_client.put(f"/api/customers/{customer_id}/", {"name": "Updated", "description": "New"})
    assert resp.status_code == 200

    # DELETE
    resp = auth_client.delete(f"/api/customers/{customer_id}/")
    assert resp.status_code == 204


def test_project_and_file_permissions(auth_client):
    customer = Customer.objects.create(name="Cust1")
    project = Project.objects.create(name="Proj1", customer=customer)

    # Upload file
    with open("./README.md", "rb") as f:
        resp = auth_client.post("./", {"project": project.id, "file": f})
    assert resp.status_code == 201
