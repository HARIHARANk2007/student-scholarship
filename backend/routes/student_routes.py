"""
FastAPI Routes for Student Operations
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from models.types import StudentProfile, MatchResult
# from database.firebase_service import get_firebase_service
from services.ocr_service import extract_text_from_file, preprocess_image
from services.gemini_service import parse_marksheet_with_ai, parse_marksheet_image_with_vision
from services.scholarship_recommendation_engine import find_matching_scholarships
import os
import tempfile
import shutil

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/test")
def test_api():
    """Simple test endpoint to verify backend is working"""
    return {"status": "Backend working"}


def get_firebase():
    return get_firebase_service()


@router.post("/", response_model=dict)
async def create_student(profile: StudentProfile):
    """Create a new student profile"""
    try:
        firebase = get_firebase()
        profile_data = profile.model_dump(by_alias=True, exclude_none=True)
        student_id = firebase.create_student_profile(profile_data)
        return {"success": True, "id": student_id, "message": "Student profile created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{student_id}", response_model=StudentProfile)
async def get_student(student_id: str):
    """Get student profile by ID"""
    try:
        firebase = get_firebase()
        profile_data = firebase.get_student_profile(student_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="Student not found")
        return StudentProfile(**profile_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{student_id}", response_model=dict)
async def update_student(student_id: str, updates: dict):
    """Update student profile"""
    try:
        firebase = get_firebase()
        success = firebase.update_student_profile(student_id, updates)
        return {"success": success, "message": "Student profile updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{student_id}", response_model=dict)
async def delete_student(student_id: str):
    """Delete student profile"""
    try:
        firebase = get_firebase()
        success = firebase.delete_student_profile(student_id)
        return {"success": success, "message": "Student profile deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[StudentProfile])
async def list_students(limit: int = 100):
    """List all student profiles"""
    try:
        firebase = get_firebase()
        profiles_data = firebase.list_student_profiles(limit)
        return [StudentProfile(**p) for p in profiles_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-marksheet", response_model=StudentProfile)
async def upload_marksheet(file: UploadFile = File(...)):
    """
    Upload marksheet image/PDF and extract student data using OCR + AI
    """
    print(f"📤 Received upload request for: {file.filename}")
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp', '.gif'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        print(f"📁 File extension: {file_ext}")
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Preprocess image if it's an image file
            processed_path = tmp_path
            if file_ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp', '.gif']:
                processed_path = preprocess_image(tmp_path)
            
            # Extract text using OCR
            print(f"📄 Extracting text from: {file.filename}")
            ocr_text = extract_text_from_file(processed_path)
            
            # Check if OCR was successful or if we need to use Vision API
            # OCR returns placeholder text starting with "[IMAGE_FILE:" when Tesseract is not available
            use_vision_api = (
                not ocr_text or 
                len(ocr_text) < 50 or 
                ocr_text.startswith("[IMAGE_FILE:") or
                ocr_text.startswith("[PDF_FILE:")
            )
            
            if use_vision_api:
                # Use Gemini Vision API to directly analyze the image
                print("🔍 OCR not available or insufficient text. Using Gemini Vision API...")
                student_profile = await parse_marksheet_image_with_vision(tmp_path)
            else:
                # Parse with AI from OCR text
                print("🤖 Parsing OCR text with AI...")
                student_profile = await parse_marksheet_with_ai(ocr_text)
            
            return student_profile
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing marksheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing marksheet: {str(e)}")


@router.post("/{student_id}/matches", response_model=List[MatchResult])
async def get_matches(student_id: str, min_score: float = 50):
    """Get scholarship matches for a student"""
    try:
        firebase = get_firebase()
        # Get student profile
        profile_data = firebase.get_student_profile(student_id)
        if not profile_data:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_profile = StudentProfile(**profile_data)
        
        # Find matching scholarships
        matches = find_matching_scholarships(student_profile, min_score)
        
        return matches
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/matches", response_model=List[MatchResult])
async def get_matches_for_profile(profile: StudentProfile, min_score: float = 50):
    """Get scholarship matches for a student profile (without saving)"""
    try:
        matches = find_matching_scholarships(profile, min_score)
        return matches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
