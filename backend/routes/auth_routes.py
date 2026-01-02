"""
Authentication Routes for Student Scholarship Application
Handles user registration, login, and token management
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from datetime import timedelta

from models.types import UserRegister, UserLogin, TokenResponse, UserRole
from services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_current_user_from_token,
    link_student_profile,
    check_admin_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to get current authenticated user from Authorization header
    
    Usage:
        @app.get("/protected")
        def protected_route(user: dict = Depends(get_current_user)):
            return {"user": user}
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = parts[1]
    user = get_current_user_from_token(token)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


async def get_optional_user(authorization: Optional[str] = Header(None)):
    """
    Dependency to optionally get current user (doesn't raise if not authenticated)
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None


async def require_admin(user: dict = Depends(get_current_user)):
    """
    Dependency to require admin role
    """
    if not check_admin_role(user):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


@router.post("/register")
def register_user(user_data: UserRegister):
    """
    Register a new user account
    
    - **email**: Valid email address (must be unique)
    - **password**: Password (min 6 characters recommended)
    - **name**: Full name
    - **role**: User role (student/admin) - defaults to student
    """
    # Check if email already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Validate password length
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )
    
    # Create user
    user = create_user(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        role=user_data.role
    )
    
    # Generate token for immediate login
    token_data = {
        "userId": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "accessToken": access_token,
        "tokenType": "bearer",
        "expiresIn": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }


@router.post("/login")
def login_user(credentials: UserLogin):
    """
    Login with email and password
    
    Returns JWT access token for authenticated requests
    """
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Generate access token
    token_data = {
        "userId": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return {
        "success": True,
        "message": "Login successful",
        "accessToken": access_token,
        "tokenType": "bearer",
        "expiresIn": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "studentId": user.get("studentId")
        }
    }


@router.get("/me")
def get_current_user_info(user: dict = Depends(get_current_user)):
    """
    Get current authenticated user's information
    
    Requires valid JWT token in Authorization header
    """
    return {
        "success": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "studentId": user.get("studentId"),
            "createdAt": user.get("createdAt"),
            "lastLogin": user.get("lastLogin")
        }
    }


@router.post("/link-student/{student_id}")
def link_student_to_user(student_id: str, user: dict = Depends(get_current_user)):
    """
    Link a student profile to the current user account
    
    This associates the user's login with their student profile for scholarship tracking
    """
    if link_student_profile(user["id"], student_id):
        return {
            "success": True,
            "message": "Student profile linked successfully",
            "userId": user["id"],
            "studentId": student_id
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


@router.post("/refresh")
def refresh_token(user: dict = Depends(get_current_user)):
    """
    Refresh the access token
    
    Use this before the current token expires to get a new one
    """
    token_data = {
        "userId": user["id"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    return {
        "success": True,
        "message": "Token refreshed",
        "accessToken": access_token,
        "tokenType": "bearer",
        "expiresIn": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/verify")
def verify_token(user: dict = Depends(get_current_user)):
    """
    Verify if the current token is valid
    
    Returns user info if token is valid
    """
    return {
        "success": True,
        "valid": True,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"]
        }
    }


# Admin-only endpoints
@router.get("/users", dependencies=[Depends(require_admin)])
def list_all_users():
    """
    List all registered users (Admin only)
    """
    from services.auth_service import users_db
    
    users = []
    for user_id, user_data in users_db.items():
        users.append({
            "id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "role": user_data["role"],
            "isActive": user_data.get("isActive", True),
            "createdAt": user_data.get("createdAt"),
            "lastLogin": user_data.get("lastLogin"),
            "studentId": user_data.get("studentId")
        })
    
    return {
        "success": True,
        "count": len(users),
        "users": users
    }
