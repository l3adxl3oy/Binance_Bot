"""
Authentication API Endpoints
Handles user signup, login, logout, and profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from database.db import get_db
from database.models import User
from api.schemas import (
    UserSignup, UserLogin, Token, UserProfile, 
    APIKeysUpdate, SuccessResponse
)
from auth.security import (
    verify_password, get_password_hash, create_access_token,
    decode_access_token, encrypt_api_key, decrypt_api_key
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==================== DEPENDENCIES ====================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode JWT token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Convert user_id to int if it's a string
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (alias for clarity)"""
    return current_user


# ==================== AUTH ENDPOINTS ====================

@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    Args:
        user_data: User signup data (username, email, password)
        
    Returns:
        JWT token and user info
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,  # Could add email verification later
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password
    
    Args:
        user_data: Login credentials (email, password)
        
    Returns:
        JWT token and user info
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email
    )


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout (client should delete token)
    
    Note: JWT tokens are stateless, so server-side logout just returns success.
    Client must delete the token from storage.
    """
    return SuccessResponse(
        success=True,
        message="Logged out successfully"
    )


@router.get("/me", response_model=UserProfile)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile
    
    Returns:
        User profile information
    """
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        has_api_keys=bool(current_user.api_key_encrypted),
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/api-keys", response_model=SuccessResponse)
async def update_api_keys(
    api_keys: APIKeysUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update Binance API keys (encrypted storage)
    
    Args:
        api_keys: Binance API key and secret
        
    Returns:
        Success message
    """
    # Encrypt API keys before storing
    encrypted_key = encrypt_api_key(api_keys.api_key)
    encrypted_secret = encrypt_api_key(api_keys.api_secret)
    
    # Update user record
    current_user.api_key_encrypted = encrypted_key
    current_user.api_secret_encrypted = encrypted_secret
    
    db.commit()
    
    return SuccessResponse(
        success=True,
        message="API keys updated successfully (encrypted)",
        data={"use_testnet": api_keys.use_testnet}
    )


@router.get("/api-keys/status")
async def get_api_keys_status(current_user: User = Depends(get_current_user)):
    """
    Check if user has configured API keys
    
    Returns:
        Status of API keys configuration
    """
    has_keys = bool(current_user.api_key_encrypted and current_user.api_secret_encrypted)
    
    return {
        "has_api_keys": has_keys,
        "message": "API keys configured" if has_keys else "No API keys configured"
    }


@router.delete("/api-keys", response_model=SuccessResponse)
async def delete_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete stored API keys
    
    Returns:
        Success message
    """
    current_user.api_key_encrypted = None
    current_user.api_secret_encrypted = None
    
    db.commit()
    
    return SuccessResponse(
        success=True,
        message="API keys deleted successfully"
    )


# ==================== UTILITY FUNCTIONS ====================

def get_user_api_keys(user: User) -> tuple[Optional[str], Optional[str]]:
    """
    Get decrypted API keys for a user
    
    Args:
        user: User model instance
        
    Returns:
        Tuple of (api_key, api_secret) or (None, None) if not configured
    """
    if not user.api_key_encrypted or not user.api_secret_encrypted:
        return None, None
    
    try:
        api_key = decrypt_api_key(user.api_key_encrypted)
        api_secret = decrypt_api_key(user.api_secret_encrypted)
        return api_key, api_secret
    except Exception as e:
        print(f"⚠️ Failed to decrypt API keys: {e}")
        return None, None
