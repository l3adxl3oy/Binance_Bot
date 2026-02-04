"""
Authentication and Security Utilities
Handles JWT tokens, password hashing, API key encryption
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os
import base64

# Password hashing - configure bcrypt to handle truncation
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # Allow bcrypt to auto-truncate passwords
)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# API Key encryption (Fernet symmetric encryption)
# In production, load this from environment variable
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against hashed password (max 72 bytes)
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches
    """
    # Bcrypt has 72 byte limit
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        plain_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt (max 72 bytes)
    
    Args:
        password: Plain text password
        
    Returns:
        Bcrypt hashed password
    """
    # Bcrypt has 72 byte limit
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token (usually {'sub': user_id})
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    # Ensure 'sub' is a string (JWT spec requires it)
    if 'sub' in to_encode and not isinstance(to_encode['sub'], str):
        to_encode['sub'] = str(to_encode['sub'])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt Binance API key using Fernet
    
    Args:
        api_key: Plain API key
        
    Returns:
        Encrypted API key (base64 encoded)
    """
    encrypted = fernet.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt Binance API key
    
    Args:
        encrypted_key: Encrypted API key (base64 encoded)
        
    Returns:
        Plain API key
    """
    encrypted = base64.b64decode(encrypted_key.encode())
    decrypted = fernet.decrypt(encrypted)
    return decrypted.decode()


def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    
    Returns:
        Base64 encoded encryption key
    """
    return Fernet.generate_key().decode()


# Example usage and testing
if __name__ == "__main__":
    # Test password hashing
    password = "test123"
    hashed = get_password_hash(password)
    print(f"Hashed password: {hashed}")
    print(f"Verify correct password: {verify_password(password, hashed)}")
    print(f"Verify wrong password: {verify_password('wrong', hashed)}")
    
    # Test JWT
    token = create_access_token({"sub": "user123"})
    print(f"\nJWT Token: {token}")
    decoded = decode_access_token(token)
    print(f"Decoded: {decoded}")
    
    # Test API key encryption
    api_key = "my-secret-binance-api-key"
    encrypted = encrypt_api_key(api_key)
    print(f"\nEncrypted API key: {encrypted}")
    decrypted = decrypt_api_key(encrypted)
    print(f"Decrypted API key: {decrypted}")
    print(f"Match: {api_key == decrypted}")
