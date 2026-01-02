"""
Authentication Service for Student Scholarship Application
Handles user registration, login, JWT tokens, and role-based access
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# JWT handling
import json
import base64
import hmac

# Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# In-memory user storage (will be replaced with Firebase)
users_db: Dict[str, Dict] = {}


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with salt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = SECRET_KEY[:16]
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Payload data to encode
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": int(expire.timestamp())})
    
    # Create JWT manually (header.payload.signature)
    header = {"alg": ALGORITHM, "typ": "JWT"}
    
    # Encode header and payload
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
    
    # Create signature
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature).decode().rstrip("=")
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            print("❌ Invalid token signature")
            return None
        
        # Decode payload (add padding if needed)
        payload_b64_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64_padded))
        
        # Check expiration
        if payload.get("exp", 0) < datetime.utcnow().timestamp():
            print("❌ Token expired")
            return None
        
        return payload
        
    except Exception as e:
        print(f"❌ Token decode error: {e}")
        return None


def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Get user by email from database
    
    Args:
        email: User email address
        
    Returns:
        User dict or None if not found
    """
    for user_id, user in users_db.items():
        if user.get("email") == email:
            return {**user, "id": user_id}
    return None


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get user by ID from database
    
    Args:
        user_id: User ID
        
    Returns:
        User dict or None if not found
    """
    if user_id in users_db:
        return {**users_db[user_id], "id": user_id}
    return None


def create_user(email: str, password: str, name: str, role: str = "student") -> Dict:
    """
    Create a new user
    
    Args:
        email: User email
        password: Plain text password
        name: User's full name
        role: User role (student/admin)
        
    Returns:
        Created user dict (without password hash)
    """
    import uuid
    
    user_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    user_data = {
        "email": email,
        "name": name,
        "passwordHash": hash_password(password),
        "role": role,
        "isActive": True,
        "createdAt": now,
        "lastLogin": None,
        "studentId": None
    }
    
    users_db[user_id] = user_data
    
    # Return user without password hash
    return {
        "id": user_id,
        "email": email,
        "name": name,
        "role": role,
        "isActive": True,
        "createdAt": now
    }


def update_user_last_login(user_id: str) -> None:
    """Update user's last login timestamp"""
    if user_id in users_db:
        users_db[user_id]["lastLogin"] = datetime.utcnow().isoformat()


def link_student_profile(user_id: str, student_id: str) -> bool:
    """
    Link a student profile to a user account
    
    Args:
        user_id: User ID
        student_id: Student profile ID
        
    Returns:
        True if successful, False otherwise
    """
    if user_id in users_db:
        users_db[user_id]["studentId"] = student_id
        return True
    return False


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with email and password
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    user = get_user_by_email(email)
    
    if not user:
        print(f"❌ User not found: {email}")
        return None
    
    if not verify_password(password, user.get("passwordHash", "")):
        print(f"❌ Invalid password for: {email}")
        return None
    
    if not user.get("isActive", True):
        print(f"❌ User account disabled: {email}")
        return None
    
    # Update last login
    update_user_last_login(user["id"])
    
    return user


def get_current_user_from_token(token: str) -> Optional[Dict]:
    """
    Get current user from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User dict if valid token, None otherwise
    """
    payload = decode_access_token(token)
    
    if not payload:
        return None
    
    user_id = payload.get("userId")
    if not user_id:
        return None
    
    return get_user_by_id(user_id)


def check_admin_role(user: Dict) -> bool:
    """Check if user has admin role"""
    return user.get("role") == "admin"


def check_student_role(user: Dict) -> bool:
    """Check if user has student role"""
    return user.get("role") == "student"


# Initialize with a default admin user
def init_default_admin():
    """Create a default admin user if none exists"""
    admin_email = "admin@scholarship.com"
    
    if not get_user_by_email(admin_email):
        create_user(
            email=admin_email,
            password="admin123",  # Change in production!
            name="System Admin",
            role="admin"
        )
        print(f"[OK] Default admin created: {admin_email}")


# Initialize on module load
init_default_admin()
