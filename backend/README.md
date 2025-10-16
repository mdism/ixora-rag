# ixora-RAG

## 🚀 Project Setup & Git Workflow

### 1. Clone the Repository

```bash
git clone https://github.com/DigitalServicesOrangeBusiness/ixora-RAG.git
cd <repo-folder>
```

### 2. Work on `develop` Branch

```bash
git checkout develop
git pull origin develop
```

### 3. Create a Feature Branch

Always branch from `develop` using the naming convention `feature/<name>` or `fix/<name>`:

```bash
git checkout -b feature/initial-backend-setup
```

### 4. Backend Setup (Python + uv)

```bash
cd backend
uv sync
uv venv   # create virtual environment with uv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
uv pip install -r requirements.txt
```

### 5. Frontend Setup (Vite)

```bash
cd frontend
npm install
npm run dev   # start frontend dev server
```

### 6. Commit & Push

```bash
git add .
git commit -m "feat: initial Django backend project setup"
git push origin feature/initial-backend-setup
```

### 7. Open a Pull Request

* Create a PR from your feature branch → `develop`.
* Wait for review and approval.
* After merging into `develop`, changes will later be merged into `main` for release.

---

### ✅ Best Practices

* Use **conventional commit messages**:

  * `feat:` → new feature
  * `fix:` → bug fix
  * `docs:` → documentation updates
  * `chore:` → maintenance tasks
* Always `git pull origin develop` before starting new work.
* Do not push directly to `main` or `develop`. Always use PRs.

---
## Hello world## Hello world## Hello world## Hello world