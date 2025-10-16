# **API Endpoint Testing Guide**

This guide provides curl commands to test all CRUD (Create, Read, Update, Delete) operations for user authentication, user management, team, and role endpoints.

**Before You Start:**

1. Ensure Django development server is running.  
2. All commands assume API is running at http://localhost:8000.

---

## **1. User Authentication**

First, We need to get a JWT access token to use for all protected routes.

### **a. Log In to Get Tokens**

This command sends a POST request to your login endpoint to get a new access and refresh token.
```
curl --location 'http://localhost:8000/api/login/'   
--header 'Content-Type: application/json'   
--data '{  
    "username": "your_username",  
    "password": "your_password"  
}'
```
**Note:** Save the access token from the response. You will need to use it in the Authorization header for all subsequent protected requests.

### **b. Refresh Access Token**

This command uses your refresh token to get a new access token.
```
curl --location 'http://localhost:8000/api/token/refresh/'   
--header 'Content-Type: application/json'   
--data '{  
    "refresh": "your_refresh_token"  
}'
```

---

## **2. User Management (Admin Only)**

These endpoints require an access token from a user with administrator privileges.

### **a. List All Users (READ)**
```
curl --location 'http://localhost:8000/api/users/'   
--header "Authorization: Bearer <access_token>"
```

### **b. Create a New User (CREATE)**

This command creates a new user account.
```
curl --location 'http://localhost:8000/api/users/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "username": "new_user",  
    "password": "strong_password_123",  
    "email": "new_user@example.com"  
}'
```

### **c. Retrieve User Details (READ)**

Replace <user_id> with the ID of the user you want to retrieve.
```
curl --location 'http://localhost:8000/api/users/<user_id>/'   
--header "Authorization: Bearer <access_token>"
```
### **d. Update User Details (UPDATE)**

Use this to update a user's information.
```
curl --location --request PATCH 'http://localhost:8000/api/users/<user_id>/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "email": "updated_email@example.com"  
}'
```

### **e. Change User Password (UPDATE)**

This uses the custom change_password endpoint.
```
curl --location --request PATCH 'http://localhost:8000/api/users/<user_id>/change_password/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "new_password": "a_new_secure_password"  
}'
```

### **f. Toggle User Status (UPDATE)**

This uses the custom toggle_status endpoint to activate or deactivate a user.
```
curl --location --request PATCH 'http://localhost:8000/api/users/<user_id>/toggle_status/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "is_active": false  
}'
```
### **g. Delete a User (DELETE)**

This permanently deletes a user account.
```
curl --location --request DELETE 'http://localhost:8000/api/users/<user_id>/'   
--header "Authorization: Bearer <access_token>"
```

---

## **3. Team Management**

These endpoints require an access token from a user with administrator privileges.

### **a. List All Teams (READ)**
```
curl --location 'http://localhost:8000/api/teams/'   
--header "Authorization: Bearer <access_token>"
```
### **b. Create a New Team (CREATE)**
```
curl --location 'http://localhost:8000/api/teams/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "name": "Frontend Engineers",  
    "description": "Team responsible for the React frontend."  
}'
```
### **c. Retrieve Team Details (READ)**
```
curl --location 'http://localhost:8000/api/teams/<team_id>/'   
--header "Authorization: Bearer <access_token>"
```
### **d. Update Team Details (UPDATE)**
```
curl --location --request PATCH 'http://localhost:8000/api/teams/<team_id>/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "name": "Frontend Team"  
}'
```

### **e. Delete a Team (DELETE)**
```
curl --location --request DELETE 'http://localhost:8000/api/teams/<team_id>/'   
--header "Authorization: Bearer <access_token>"
```

### *f. Add a Member to a Team (UPDATE)*
This custom endpoint adds a user to an existing team. You need to provide the team_id and the user_id in the request body.

```
curl --location --request POST 'http://localhost:8000/api/teams/<team_id>/add_member/' 
--header "Authorization: Bearer <access_token>" 
--header 'Content-Type: application/json' 
--data '{
    "user_id": <user_id>
}'
```



---

## **4. Role Management**

These endpoints are for managing roles and require an administrator token.

### **a. List All Roles (READ)**
```
curl --location 'http://localhost:8000/api/roles/'   
--header "Authorization: Bearer <access_token>"
```
### **b. Create a New Role (CREATE)**
```
curl --location 'http://localhost:8000/api/roles/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "name": "Admin",  
    "description": "Administrator with full access."  
}'
```
### **c. Retrieve Role Details (READ)**
```
curl --location 'http://localhost:8000/api/roles/<role_id>/'   
--header "Authorization: Bearer <access_token>"
```
### **d. Update Role Details (UPDATE)**
```
curl --location --request PATCH 'http://localhost:8000/api/roles/<role_id>/'   
--header "Authorization: Bearer <access_token>"   
--header 'Content-Type: application/json'   
--data '{  
    "name": "Administrator"  
}'
```
### **e. Delete a Role (DELETE)**
```
curl --location --request DELETE 'http://localhost:8000/api/roles/<role_id>/'  
--header "Authorization: Bearer <access_token>"  
```

---