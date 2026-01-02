"""
Data Models for Student Scholarship Application
Python equivalents of TypeScript types using Pydantic
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class SubjectMark(BaseModel):
    """Individual subject marks"""
    subject: str
    score: float
    max_score: float = Field(default=100.0, alias="maxScore")

    class Config:
        populate_by_name = True


class Gender(str, Enum):
    """Gender options"""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"
    PREFER_NOT_TO_SAY = "Prefer Not to Say"


class Category(str, Enum):
    """Student category/caste classification"""
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    GENERAL = "General"
    EWS = "EWS"


class ExtractionMethod(str, Enum):
    """Method used to create student profile"""
    AI = "AI"
    OCR = "OCR"
    MANUAL = "Manual"


class StudentProfile(BaseModel):
    """Complete student profile with academic and demographic information"""
    # Basic Info
    id: Optional[str] = None  # Firebase document ID
    name: str
    date_of_birth: Optional[str] = Field(None, alias="dateOfBirth")  # ISO format: YYYY-MM-DD
    gender: Optional[Gender] = None
    
    # Academic Info
    age: Optional[int] = None
    region: str
    education_level: Optional[str] = Field(None, alias="educationLevel")  # e.g., "10th", "12th", "Bachelor"
    marks: List[SubjectMark] = []
    overall_percentage: float = Field(alias="overallPercentage")
    
    # Financial & Social Info
    income_level: str = Field(alias="incomeLevel")  # e.g., "< 2 LPA", "< 5 LPA"
    family_annual_income: Optional[float] = Field(None, alias="familyAnnualIncome")
    parent_occupation: Optional[str] = Field(None, alias="parentOccupation")
    is_first_graduate: Optional[bool] = Field(None, alias="isFirstGraduate")
    category: Optional[Category] = None
    religion: Optional[str] = None
    
    # Additional Info
    extracted_from_doc: Optional[bool] = Field(False, alias="extractedFromDoc")
    created_at: Optional[str] = Field(None, alias="createdAt")
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    extraction_method: Optional[ExtractionMethod] = Field(None, alias="extractionMethod")
    
    class Config:
        populate_by_name = True
        use_enum_values = True


class Scholarship(BaseModel):
    """Scholarship opportunity"""
    id: str
    title: str
    provider: str
    amount: str
    deadline: str
    category: str
    criteria: str
    tags: List[str] = []
    apply_url: Optional[str] = Field(None, alias="applyUrl")
    
    class Config:
        populate_by_name = True


class MatchResult(Scholarship):
    """Scholarship with match score and reasoning"""
    match_score: float = Field(alias="matchScore")  # 0-100
    reason: str
    autofill_statement: str = Field(alias="autofillStatement")
    is_web_find: Optional[bool] = Field(False, alias="isWebFind")
    source_url: Optional[str] = Field(None, alias="sourceUrl")
    
    class Config:
        populate_by_name = True


class ApplicationStatus(str, Enum):
    """Application status options"""
    PENDING = "Pending"
    VERIFIED = "Verified"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class StudentApplication(BaseModel):
    """Student scholarship application"""
    id: str
    student_id: Optional[str] = Field(None, alias="studentId")
    student_name: str = Field(alias="studentName")
    region: str
    scholarship_name: str = Field(alias="scholarshipName")
    category: str
    applied_at: str = Field(alias="appliedAt")  # ISO Date
    status: ApplicationStatus
    match_score: float = Field(alias="matchScore")
    income: str
    
    class Config:
        populate_by_name = True
        use_enum_values = True


class Language(str, Enum):
    """Supported languages"""
    ENGLISH = "English"
    HINDI = "Hindi"
    TAMIL = "Tamil"


class AppView(str, Enum):
    """Application view states"""
    LOGIN = "LOGIN"
    LANDING = "LANDING"
    ONBOARDING = "ONBOARDING"
    UPLOAD = "UPLOAD"
    MATCHES = "MATCHES"
    DASHBOARD = "DASHBOARD"


# ==================== AUTHENTICATION MODELS ====================

class UserRole(str, Enum):
    """User role types"""
    STUDENT = "student"
    ADMIN = "admin"


class UserRegister(BaseModel):
    """User registration request"""
    email: str
    password: str
    name: str
    role: UserRole = UserRole.STUDENT
    
    class Config:
        use_enum_values = True


class UserLogin(BaseModel):
    """User login request"""
    email: str
    password: str


class User(BaseModel):
    """User model (stored in database)"""
    id: Optional[str] = None
    email: str
    name: str
    password_hash: str = Field(alias="passwordHash")
    role: UserRole = UserRole.STUDENT
    is_active: bool = Field(default=True, alias="isActive")
    created_at: Optional[str] = Field(None, alias="createdAt")
    last_login: Optional[str] = Field(None, alias="lastLogin")
    student_id: Optional[str] = Field(None, alias="studentId")  # Link to student profile
    
    class Config:
        populate_by_name = True
        use_enum_values = True


class TokenResponse(BaseModel):
    """JWT Token response"""
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    expires_in: int = Field(alias="expiresIn")  # seconds
    user: dict
    
    class Config:
        populate_by_name = True


class TokenData(BaseModel):
    """Data encoded in JWT token"""
    user_id: str = Field(alias="userId")
    email: str
    role: UserRole
    exp: int  # expiration timestamp
    
    class Config:
        populate_by_name = True
        use_enum_values = True
