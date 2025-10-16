Perfect 👍 You’re asking the right thing at the right time.
Since we already have Django REST Framework (DRF) viewsets, you can test **CRUD** operations with tools like:

* **Postman / Insomnia** → for manual API testing
* **pytest + DRF’s APIClient** → for automated testing

Let’s cover **both**:

---

# 🔹 1. Manual Testing with Postman

## 🔐 Authentication

* First, log in to get your JWT token (assuming you’re using `djangorestframework-simplejwt`):

```
POST /api/token/
{
  "username": "admin",
  "password": "adminpass"
}
```

Response:

```json
{
  "access": "your.jwt.access.token",
  "refresh": "your.jwt.refresh.token"
}
```

Set `Authorization: Bearer <access>` header in all following requests.

---

## 📂 Endpoints (CRUD)

### Customers

* **Create**

  ```
  POST /api/customers/
  { "name": "Acme Corp", "description": "Test customer" }
  ```
* **List**

  ```
  GET /api/customers/
  ```
* **Retrieve**

  ```
  GET /api/customers/1/
  ```
* **Update**

  ```
  PUT /api/customers/1/
  { "name": "Acme Corp Updated", "description": "New desc" }
  ```
* **Delete**

  ```
  DELETE /api/customers/1/
  ```

---

### Projects

* **Create**

  ```
  POST /api/projects/
  { "customer": 1, "name": "Project Alpha", "description": "First project" }
  ```
* **List (only user’s projects)**

  ```
  GET /api/projects/
  ```
* **Update**

  ```
  PUT /api/projects/1/
  { "customer": 1, "name": "Project Alpha Updated", "description": "Updated project" }
  ```

---

### UserProject (assign users to projects)

* **Assign User**

  ```
  POST /api/user-projects/
  { "user": 2, "project": 1, "role": "member" }
  ```
* **Update Role**

  ```
  PATCH /api/user-projects/1/
  { "role": "owner" }
  ```
* **Delete Assignment**

  ```
  DELETE /api/user-projects/1/
  ```

---

### Files (with permissions)

* **Upload**

  ```
  POST /api/files/
  FormData: 
    project = 1
    file = <choose file>
  ```
* **List project files**

  ```
  GET /api/files/?project=1
  ```
* **Delete**

  ```
  DELETE /api/files/1/
  ```

---

### Chat Sessions

* **Create**

  ```
  POST /api/chat-sessions/
  { "project": 1, "title": "Discussion 1" }
  ```
* **List**

  ```
  GET /api/chat-sessions/?project=1
  ```

### Chat Messages

* **Add message**

  ```
  POST /api/chat-messages/
  { "session": 1, "sender": 2, "message": "Hello team" }
  ```
* **List**

  ```
  GET /api/chat-messages/?session=1
  ```

---

# 🔹 2. Automated Testing (pytest + DRF APIClient)

Install pytest:

```bash
pip install pytest pytest-django
```

## `tests/test_api.py`

```python
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from project.models import Customer, Project, UserProject

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
    with open("README.md", "rb") as f:
        resp = auth_client.post("/api/files/", {"project": project.id, "file": f})
    assert resp.status_code == 201
```

Run tests:

```bash
pytest -v
```

---

⚡ With this setup:

* You can manually test with Postman/Insomnia.
* You can automate regression testing with pytest.

---

Do you want me to also generate a **ready-made Postman collection JSON** for you, so you can just import it and start hitting these endpoints?
