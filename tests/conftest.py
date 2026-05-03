import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.main import app
from app.database import Base, get_db

# 1. SETUP: Creating an In-memory DB for speed & no footprint
SQL_ALCHEMY_DATABASE_URL = "postgresql://ledger_admin:abc123@localhost:5433/fintech_ledger_test"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. OVERRIDE: With this FastAPI will now connect to a fake DB for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
    
app.dependency_overrides[get_db] = override_get_db

# 3. GLOBAL CLIENT FIXTURE
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

# 4. DATABASE FIXTURES
@pytest.fixture(autouse=True)
def setup_database():
    """Secures a clean slate before every test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. DATA FIXTURES
@pytest.fixture
def test_admin_user(test_db):
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("adminpass123")

    admin = models.User(
        username="admin_user",
        password_hash=hashed_pw,
        role="Admin",
        is_active=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def seeded_records(test_db, test_admin_user):
    records = [
        models.Record(amount=25000, category="Housing", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=1500, category="Utilities", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=500, category="Food", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=97000.5, category="Salary", record_type="income", user_id=test_admin_user.id),
    ]
    test_db.add_all(records)
    test_db.commit()
    return test_db

@pytest.fixture
def authorized_client(client, test_admin_user):
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin_user", "password": "adminpass123"}
    )
    token = res.json()["access_token"]
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token}"}
    return auth_client

@pytest.fixture
def deactivated_user(test_db):
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("testpass123")
    user = models.User(
        username="fired_analyst",
        password_hash=hashed_pw,
        role="Analyst",
        is_active=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user