## 🔹 Test on Postman

1. **Setup Authentication**

   * First, log in with your API login endpoint (probably `/api/token/` if you’re using JWT).
   * Copy the `access_token`.
   * In Postman, under **Authorization → Bearer Token**, paste the token.

---

2. **Test Customer CRUD**

   * `POST /customers/` → Create customer

     ```json
     { "name": "Customer1", "contact": "cust1@example.com" }
     ```

   * `GET /customers/` → List customers

   * `GET /customers/1/` → Retrieve

   * `PUT /customers/1/` → Update

   * `DELETE /customers/1/` → Delete

   * Extra endpoint:

     * `GET /customers/1/documents/` → Documents under this customer
     * `GET /customers/1/tags/` → Tags under this customer

---

3. **Test Tags**

   * `POST /tags/` → Create

     ```json
     { "name": "infra" }
     ```
   * `GET /tags/` → List tags
   * `GET /tags/1/documents/` → Documents linked to this tag

---

4. **Test Documents**

   * `POST /documents/` → Upload document

     * Use **form-data** in Postman
     * Keys:

       * `file_name` → "Firewall Guide"
       * `file` → (choose file)
       * `customer` → `1`
       * `tag` → `1`
   * `GET /documents/` → List
   * `GET /documents/my-documents/` → All docs the logged-in user can access

---

5. **Test UserTagAssignment**

   * `POST /usertagassignments/` → Assign user to a tag

     ```json
     { "user": 2, "tag": 1, "role": "viewer" }
     ```
   * `GET /usertagassignments/` → List assignments

---

6. **Test Chat**

   * `POST /chatsessions/` → Start chat session

     ```json
     { "user": 2, "customer": 1, "tag": 1 }
     ```
   * `GET /chatsessions/my-sessions/` → List user’s sessions
   * `POST /chatmessages/` → Add message

     ```json
     { "session": 1, "sender": "user", "message": "Hello AI!" }
     ```

---

