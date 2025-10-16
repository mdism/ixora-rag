📂 Endpoints (CRUD)

### **Authentication**

**Login**
```
* **POST** /api/login/  
* { "username": "your_username", "password": "your_password" }
```
**Refresh Token**
```
* **POST** /api/token/refresh/  
* { "refresh": "your_refresh_token" }
```
---
### **Users**

**List**
```
* **GET** /api/users/
```
**Create**
```
* **POST** /api/users/  
* { "username": "new_user", "password": "password123", "email": "new_user@example.com" }
```
**Retrieve**
```
* **GET** /api/users/<user_id>/
```
**Update**
```
* **PATCH** /api/users/<user_id>/  
* { "email": "updated_email@example.com" }
```
**Change Password**
```
* **PATCH** /api/users/<user_id>/change_password/  
* { "new_password": "a_new_secure_password" }
```
**Toggle Status**
```
* **PATCH** /api/users/<user_id>/toggle_status/  
* { "is_active": false }
```
**Delete**
```
* **DELETE** /api/users/<user_id>/
```

---
### **Teams**

**List**
```
* **GET** /api/teams/
```
**Create**
```
* **POST** /api/teams/  
* { "name": "Frontend Team", "description": "Responsible for frontend development." }
```
**Retrieve**
```
* **GET** /api/teams/<team_id>/
```
**Update**
```
* **PATCH** /api/teams/<team_id>/  
* { "description": "The new description for the team." }
```
**Delete**
```
* **DELETE** /api/teams/<team_id>/
```
**Add Member**
```
* **POST** /api/teams/<team_id>/add_member/  
* { "user_id": <user_id> }
```
---
### **Roles**

**List**
```
* **GET** /api/roles/
```
**Create**
```
* **POST** /api/roles/  
* { "name": "Admin", "description": "Full administrative access." }
```
**Retrieve**
```
* **GET** /api/roles/<role_id>/
```
**Update**
```
* **PATCH** /api/roles/<role_id>/  
* { "name": "Administrator" }
```
**Delete**
```
* **DELETE** /api/roles/<role_id>/
```


----- 
### testing pending see alternate document [test Company, projects and file rested API end pointsI](../project_management/test_API.md) 
### **Companies**

**List**
```
* **GET** /api/companies/
```
**Create**
```
* **POST** /api/companies/  
* { "name": "Acme Corp", "description": "A new company." }
```
**Retrieve**
```
* **GET** /api/companies/<company_id>/
```
**Update**
```
* **PATCH** /api/companies/<company_id>/  
* { "name": "Acme Inc." }
```
**Delete**
```
* **DELETE** /api/companies/<company_id>/
```
---
### **Projects**

**List**
```
* **GET** /api/projects/
```
**Create**
```
* **POST** /api/projects/  
* { "name": "Project Alpha", "description": "A new project.", "company": <company_id> }
```
**Retrieve**
```
* **GET** /api/projects/<project_id>/
```
**Update**
```
* **PATCH** /api/projects/<project_id>/  
* { "name": "Project Beta" }
```
**Delete**
```
* **DELETE** /api/projects/<project_id>/
```
---
### **Files**

**List**
```
* **GET** /api/files/
```
**Upload**
```
* **POST** /api/files/  
* { "file": <file_data>, "project": <project_id> }
```
**Retrieve**
```
* **GET** /api/files/<file_id>/
```
**Delete**
```
* **DELETE** /api/files/<file_id>/
```