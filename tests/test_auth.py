"""
Test Authentication System
Run: pytest tests/test_auth.py -v
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_db
from database.models import Base, User, BotConfig
from auth.security import get_password_hash, verify_password, encrypt_api_key, decrypt_api_key

# Test database (in-memory SQLite with single connection)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once at module level
Base.metadata.create_all(bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Import app and setup
from fastapi import FastAPI
from api.auth import router as auth_router
from api.configs import router as configs_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(configs_router)
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Clean database after each test"""
    yield
    # Delete all rows from tables (but keep schema)
    db = TestingSessionLocal()
    try:
        # Delete in correct order to avoid FK constraint issues
        db.query(BotConfig).delete()
        db.query(User).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


class TestPasswordHashing:
    """Test password hashing functions"""
    
    def test_password_hash_and_verify(self):
        """Test password hashing and verification"""
        password = "test123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)


class TestAPIKeyEncryption:
    """Test API key encryption"""
    
    def test_encrypt_decrypt_api_key(self):
        """Test API key encryption and decryption"""
        api_key = "my-secret-binance-api-key-12345"
        
        encrypted = encrypt_api_key(api_key)
        assert encrypted != api_key
        
        decrypted = decrypt_api_key(encrypted)
        assert decrypted == api_key


class TestUserSignup:
    """Test user signup"""
    
    def test_signup_success(self, test_db):
        """Test successful signup"""
        response = client.post("/auth/signup", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["user_id"] > 0
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    def test_signup_duplicate_email(self, test_db):
        """Test signup with duplicate email"""
        # First signup
        client.post("/auth/signup", json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        
        # Second signup with same email
        response = client.post("/auth/signup", json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_signup_duplicate_username(self, test_db):
        """Test signup with duplicate username"""
        # First signup
        client.post("/auth/signup", json={
            "username": "sameuser",
            "email": "user1@example.com",
            "password": "password123"
        })
        
        # Second signup with same username
        response = client.post("/auth/signup", json={
            "username": "sameuser",
            "email": "user2@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]


class TestUserLogin:
    """Test user login"""
    
    def test_login_success(self, test_db):
        """Test successful login"""
        # Signup first
        client.post("/auth/signup", json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "password123"
        })
        
        # Login
        response = client.post("/auth/login", json={
            "email": "login@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_db):
        """Test login with wrong password"""
        # Signup first
        client.post("/auth/signup", json={
            "username": "user",
            "email": "user@example.com",
            "password": "correct123"
        })
        
        # Login with wrong password
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "wrong123"
        })
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, test_db):
        """Test login with non-existent user"""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401


class TestUserProfile:
    """Test user profile endpoints"""
    
    def test_get_profile(self, test_db):
        """Test getting user profile"""
        # Signup and get token
        signup_response = client.post("/auth/signup", json={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "password123"
        })
        token = signup_response.json()["access_token"]
        
        # Get profile
        response = client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "profileuser"
        assert data["email"] == "profile@example.com"
        assert data["is_active"] is True
        assert data["has_api_keys"] is False
    
    def test_get_profile_unauthorized(self, test_db):
        """Test getting profile without token"""
        response = client.get("/auth/me")
        
        assert response.status_code == 401


class TestAPIKeys:
    """Test API key management"""
    
    def test_update_api_keys(self, test_db):
        """Test updating API keys"""
        # Signup and get token
        signup_response = client.post("/auth/signup", json={
            "username": "apikeyuser",
            "email": "apikey@example.com",
            "password": "password123"
        })
        token = signup_response.json()["access_token"]
        
        # Update API keys
        response = client.post("/auth/api-keys", 
            headers={"Authorization": f"Bearer {token}"},
            json={
                "api_key": "test-api-key-12345",
                "api_secret": "test-api-secret-67890",
                "use_testnet": True
            }
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Check status
        status_response = client.get("/auth/api-keys/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert status_response.json()["has_api_keys"] is True
    
    def test_delete_api_keys(self, test_db):
        """Test deleting API keys"""
        # Signup and get token
        signup_response = client.post("/auth/signup", json={
            "username": "deleteuser",
            "email": "delete@example.com",
            "password": "password123"
        })
        token = signup_response.json()["access_token"]
        
        # Add API keys
        client.post("/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "api_key": "test-key",
                "api_secret": "test-secret",
                "use_testnet": True
            }
        )
        
        # Delete API keys
        response = client.delete("/auth/api-keys",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Check status
        status_response = client.get("/auth/api-keys/status",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert status_response.json()["has_api_keys"] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
