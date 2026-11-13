# 🩺 MediFlow Backend

### Clinical Workflow Intelligence — the engine behind modern care.

Hospitals don't run on paperwork. They run on **flow**: the right person, with the right access, at the right moment. **MediFlow** is a multi-tenant clinical workflow platform, and this repository is its backbone: a fast, typed, production-minded API that gives every clinic, hospital, and health network its own secure space, with its own people, roles, and permissions, on a single shared platform.

Built on **FastAPI**, **SQLAlchemy 2** and **PostgreSQL**. Authenticated with **JWT**. Versioned with **Alembic**. Designed so the next feature plugs in cleanly instead of fighting the last one.

---

## ✨ Highlights

- 🏥 **Multi-tenant by design.** Every organisation is a tenant, and users, roles and data are scoped to it.
- 🔐 **JWT authentication.** Bcrypt-hashed passwords, bearer tokens, and an active-user check on protected routes.
- 🛡️ **Granular RBAC.** Roles map to permissions (`resource` + `action`), and permissions can be assigned per role.
- 👑 **Super Admin tier.** Tenant and permission management are locked to the platform Super Admin.
- 📚 **Master codes.** Central lookup data (e.g. gender, payment status) served from a single settings API.
- 🧯 **Consistent errors.** Every failure returns the same JSON shape with a correlation `token` that matches the server log line. DB unique violations become clean `409`s and internals never leak.
- 🧬 **Migration-first schema.** Every table change is a reviewable Alembic revision.
- 📖 **Interactive docs.** Swagger UI and ReDoc are available out of the box.

---

## 🧱 Tech Stack

| Layer | Choice |
| --- | --- |
| Language | Python 3.12 |
| Framework | FastAPI + Uvicorn |
| ORM / Migrations | SQLAlchemy 2.0 + Alembic |
| Database | PostgreSQL (`psycopg2`) |
| Validation / Config | Pydantic v2 + pydantic-settings |
| Auth | python-jose (JWT) + passlib / bcrypt |

---

## 🗂️ Project Structure

```
mediflow-backend/
├── alembic/                # Migration environment + versions
├── app/
│   ├── main.py             # App factory, CORS, error handlers, routers
│   ├── api/                # Route handlers (auth, users, tenants, roles, permissions, settings)
│   ├── core/               # config, database, security, dependencies, constants, messages, exceptions
│   ├── crud/               # Database access layer
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic request/response schemas
│   ├── services/           # Business logic (reserved)
│   └── scripts/            # CLI helpers (e.g. create_super_admin)
├── tests/                  # Pytest suite
├── alembic.ini
├── requirements.txt
└── package.json            # Convenience dev/start scripts
```

---

## 🚀 Getting Started

### Prerequisites

- Python **3.12**
- A running **PostgreSQL** instance

### 1. Clone & install

```bash
git clone <your-repo-url>
cd mediflow-backend

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mediflow
SECRET_KEY=change-me-to-a-long-random-string

# Optional
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
DEBUG=false
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

> `DATABASE_URL` and `SECRET_KEY` are required. The app won't start without them. Never commit `.env`.

### 3. Run migrations

```bash
alembic upgrade head
```

### 4. Create your first Super Admin

User-creation endpoints require a logged-in Super Admin, so the first one comes from the CLI:

```bash
python -m app.scripts.create_super_admin
```

### 5. Launch

```bash
uvicorn app.main:app --reload
# or on Windows, via the bundled script
npm run dev
```

The API is live at **http://127.0.0.1:8000**

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

---

## 🔌 API Overview

| Area | Prefix | Access |
| --- | --- | --- |
| Authentication | `/auth` | `POST /login`, `GET /me` |
| Users | `/users` | CRUD, plus activate / deactivate |
| Tenants | `/tenants` | Super Admin only, CRUD plus status toggle |
| Roles | `/roles` | CRUD, status toggle, role ↔ permission assignment |
| Permissions | `/permissions` | Super Admin only, CRUD by code |
| Master Codes | `/settings/master-codes` | Any active user, read-only lookups |

Full request/response schemas live in the interactive docs at `/docs`.

### Error format

Every error returns the same envelope:

```json
{
  "id": "6f1c…",
  "message": "Email already exists",
  "status_code": 409,
  "token": "a-request-id-or-generated-uuid",
  "success": false
}
```

Send an `X-Request-ID` header and it comes back as `token`, so you can match a client-side failure to the server log line.

---

## 🧪 Testing

```bash
pip install pytest httpx
pytest
```

---

## 🛠️ Database Migrations

```bash
# Create a new revision after changing models
alembic revision --autogenerate -m "describe your change"

# Apply
alembic upgrade head

# Roll back one step
alembic downgrade -1
```

---

## 📄 License

Released under the [MIT License](LICENSE).

---

<p align="center"><b>MediFlow</b>: less friction, more care. 💙</p>
