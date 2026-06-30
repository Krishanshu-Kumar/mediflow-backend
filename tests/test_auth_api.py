import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.main import app
from app.core.database import Base, get_db
# Import all models to ensure they are registered with Base.metadata
from app.models.Users.tenant_model import Tenant
from app.models.Users.role_model import Role
from app.models.Users.auth_users_model import AuthUser
from app.models.Settings.master_codes import MasterCode

# Custom SQLite compiler for JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


from sqlalchemy.pool import StaticPool

# SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="module")
def db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception as e:
            print("Error dropping tables:", e)



@pytest.fixture(scope="module")
def client(db):
    # Override get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_auth_and_user_flow(client, db):
    # 1. Create a mock tenant and role in the database for the test
    tenant_id = uuid4()
    role_id = uuid4()

    db_tenant = Tenant(
        id=tenant_id,
        name="Test Hospital",
        slug="test-hospital",
        plan_code=1001,
    )
    db.add(db_tenant)

    db_role = Role(
        id=role_id,
        designation_code=100,
        designation_group_code=10,
        name="Clinician",
        display_name="Medical Clinician",
    )
    db.add(db_role)
    db.commit()

    # 2. Test User Registration (/auth/register)
    user_payload = {
        "tenant_id": str(tenant_id),
        "role_id": str(role_id),
        "email": "doctor@hospital.com",
        "password": "securepassword123",
        "full_name": "Dr. John Doe",
        "phone": "+15550199",
        "is_active": True,
        "is_verified": False,
    }

    response = client.post("/auth/register", json=user_payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == "doctor@hospital.com"
    assert data["full_name"] == "Dr. John Doe"
    assert "id" in data
    user_uuid = data["id"]

    # Try registering again with duplicate email (should fail)
    response = client.post("/auth/register", json=user_payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

    # 3. Test Login (/auth/login)
    login_payload = {
        "tenant_id": str(tenant_id),
        "email": "doctor@hospital.com",
        "password": "securepassword123",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200, response.text
    login_data = response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"
    token = login_data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # 4. Test Get Current User (/auth/me)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    me_data = response.json()
    assert me_data["email"] == "doctor@hospital.com"
    assert me_data["id"] == user_uuid

    # 5. Test Get Users List (/users/)
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200, response.text
    users_list = response.json()
    assert len(users_list) >= 1
    assert users_list[0]["email"] == "doctor@hospital.com"

    # 6. Test Update User (/users/{user_id})
    update_payload = {
        "full_name": "Dr. John H. Doe",
        "phone": "+15559999",
    }
    response = client.put(f"/users/{user_uuid}", json=update_payload, headers=headers)
    assert response.status_code == 200, response.text
    updated_data = response.json()
    assert updated_data["full_name"] == "Dr. John H. Doe"
    assert updated_data["phone"] == "+15559999"

    # 7. Test Deactivate User (should not be allowed to self-deactivate)
    response = client.patch(f"/users/{user_uuid}/deactivate", headers=headers)
    assert response.status_code == 400
    assert "Self-deactivation" in response.json()["detail"]

    # Create another user in the same tenant to test deactivation
    other_user_payload = {
        "tenant_id": str(tenant_id),
        "role_id": str(role_id),
        "email": "nurse@hospital.com",
        "password": "password123",
        "full_name": "Nurse Jane",
        "phone": "+15550211",
        "is_active": True,
        "is_verified": False,
    }
    response = client.post("/auth/register", json=other_user_payload)
    assert response.status_code == 201
    other_user_uuid = response.json()["id"]

    # Deactivate the other user
    response = client.patch(f"/users/{other_user_uuid}/deactivate", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is False

    # Try logging in with the deactivated user (should fail)
    other_login_payload = {
        "tenant_id": str(tenant_id),
        "email": "nurse@hospital.com",
        "password": "password123",
    }
    response = client.post("/auth/login", json=other_login_payload)
    assert response.status_code == 400
    assert "inactive" in response.json()["detail"].lower()

    # Reactivate the other user
    response = client.patch(f"/users/{other_user_uuid}/activate", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["is_active"] is True

    # Try logging in again (should now succeed)
    response = client.post("/auth/login", json=other_login_payload)
    assert response.status_code == 200
