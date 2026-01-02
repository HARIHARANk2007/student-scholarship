"""
Student Scholarship Backend API
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
import uuid
import os
import tempfile
import shutil

from models.types import StudentProfile, ApplicationStatus
from services.ocr_service import extract_text_from_file, preprocess_image
from services.scholarship_recommendation_engine import (
    SCHOLARSHIPS_DATABASE, 
    find_matching_scholarships, 
    get_scholarship_by_id
)
from services.firebase_service import (
    initialize_firebase,
    create_student as fb_create_student,
    get_student as fb_get_student,
    update_student as fb_update_student,
    delete_student as fb_delete_student,
    list_students as fb_list_students,
    create_application as fb_create_application,
    get_application as fb_get_application,
    update_application as fb_update_application,
    delete_application as fb_delete_application,
    list_applications as fb_list_applications,
    FIREBASE_AVAILABLE
)

# Import authentication routes
from routes.auth_routes import router as auth_router, get_current_user, get_optional_user, require_admin

app = FastAPI(
    title="Student Scholarship API",
    description="API for student scholarship management and recommendations with authentication",
    version="1.0.0"
)

# Include authentication routes
app.include_router(auth_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase on startup
USE_FIREBASE = False  # Will be set to True if Firebase initializes successfully

@app.on_event("startup")
async def startup_event():
    global USE_FIREBASE
    if FIREBASE_AVAILABLE:
        if initialize_firebase():
            USE_FIREBASE = True
            print("[OK] Firebase ENABLED - Data will persist!")
        else:
            print("[WARN] Firebase failed - Using in-memory storage")
    else:
        print("[WARN] Firebase not available - Using in-memory storage")

# In-memory storage (fallback when Firebase unavailable)
students_db: dict[str, dict] = {}
applications_db: dict[str, dict] = {}


@app.get("/")
def root():
    return {
        "message": "Student Scholarship API is running",
        "storage": "Firebase (persistent)" if USE_FIREBASE else "In-memory (temporary)"
    }


@app.get("/api/students/test")
def test_api():
    """Simple test endpoint to verify backend is working"""
    return {
        "status": "Backend working",
        "storage": "Firebase" if USE_FIREBASE else "In-memory"
    }


# ==================== STUDENT APIs ====================

@app.post("/api/students/register")
def register_student(profile: StudentProfile):
    """
    Register a new student profile (stored in Firebase if available)
    """
    # Set timestamps
    now = datetime.utcnow().isoformat()
    
    # Prepare student data
    student_data = profile.model_dump(by_alias=True, exclude_none=True)
    student_data["createdAt"] = now
    student_data["updatedAt"] = now
    
    if USE_FIREBASE:
        # Store in Firebase (persistent)
        student_id = fb_create_student(student_data)
        if not student_id:
            raise HTTPException(status_code=500, detail="Failed to save to Firebase")
    else:
        # Fallback to in-memory
        student_id = str(uuid.uuid4())
        student_data["id"] = student_id
        students_db[student_id] = student_data
    
    student_data["id"] = student_id
    
    return {
        "success": True,
        "message": "Student registered successfully",
        "studentId": student_id,
        "storage": "Firebase" if USE_FIREBASE else "In-memory",
        "data": student_data
    }


@app.get("/api/students/{student_id}")
def get_student_profile(student_id: str):
    """
    Get student profile by ID
    """
    if USE_FIREBASE:
        student_data = fb_get_student(student_id)
        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found")
        student_data = students_db[student_id]
    
    return {
        "success": True,
        "data": student_data
    }


@app.put("/api/students/{student_id}")
def update_student_profile(student_id: str, profile: StudentProfile):
    """
    Update an existing student profile
    """
    # Prepare update data
    student_data = profile.model_dump(by_alias=True, exclude_none=True)
    student_data["updatedAt"] = datetime.utcnow().isoformat()
    
    if USE_FIREBASE:
        existing = fb_get_student(student_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_data["id"] = student_id
        student_data["createdAt"] = existing.get("createdAt")
        
        if not fb_update_student(student_id, student_data):
            raise HTTPException(status_code=500, detail="Failed to update in Firebase")
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_data["id"] = student_id
        student_data["createdAt"] = students_db[student_id].get("createdAt")
        students_db[student_id] = student_data
    
    return {
        "success": True,
        "message": "Student profile updated successfully",
        "data": student_data
    }


@app.delete("/api/students/{student_id}")
def delete_student(student_id: str):
    """
    Delete a student profile
    """
    if USE_FIREBASE:
        existing = fb_get_student(student_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Student not found")
        
        if not fb_delete_student(student_id):
            raise HTTPException(status_code=500, detail="Failed to delete from Firebase")
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found")
        students_db.pop(student_id)
    
    return {
        "success": True,
        "message": "Student deleted successfully",
        "deletedId": student_id
    }


@app.get("/api/students")
def list_all_students(limit: int = 100, skip: int = 0):
    """
    List all registered students (with pagination)
    """
    if USE_FIREBASE:
        all_students = fb_list_students(limit=limit, offset=skip)
        total = len(all_students)  # Note: Firebase doesn't give total easily
    else:
        all_students = list(students_db.values())
        total = len(all_students)
        # Apply pagination for in-memory
        all_students = all_students[skip:skip + limit]
    
    return {
        "success": True,
        "total": total,
        "count": len(all_students),
        "skip": skip,
        "limit": limit,
        "storage": "Firebase" if USE_FIREBASE else "In-memory",
        "students": all_students
    }


# ==================== OCR APIs ====================

# In-memory storage for uploaded files
uploads_db: dict[str, dict] = {}


@app.post("/api/ocr/upload")
async def upload_marksheet(file: UploadFile = File(...)):
    """
    Upload a marksheet image or PDF for OCR processing
    """
    # Validate file type
    allowed_types = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
        )
    
    # Generate unique ID for this upload
    upload_id = str(uuid.uuid4())
    
    # Create temp directory if not exists
    temp_dir = os.path.join(tempfile.gettempdir(), "scholarship_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(temp_dir, f"{upload_id}{file_ext}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Store upload info
        uploads_db[upload_id] = {
            "id": upload_id,
            "filename": file.filename,
            "filePath": file_path,
            "fileType": file_ext,
            "uploadedAt": datetime.utcnow().isoformat(),
            "status": "uploaded"
        }
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "uploadId": upload_id,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")


@app.post("/api/ocr/extract/{upload_id}")
async def extract_text(upload_id: str):
    """
    Extract text from an uploaded marksheet using OCR
    """
    if upload_id not in uploads_db:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    upload_info = uploads_db[upload_id]
    file_path = upload_info["filePath"]
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File no longer exists")
    
    try:
        # Preprocess image for better OCR (only for images, not PDFs)
        if upload_info["fileType"] != ".pdf":
            preprocess_image(file_path)
        
        # Extract text
        extracted_text = extract_text_from_file(file_path)
        
        # Update status
        uploads_db[upload_id]["status"] = "extracted"
        uploads_db[upload_id]["extractedText"] = extracted_text
        
        return {
            "success": True,
            "uploadId": upload_id,
            "filename": upload_info["filename"],
            "extractedText": extracted_text,
            "characterCount": len(extracted_text)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")


# ==================== SCHOLARSHIP APIs ====================

@app.get("/api/scholarships")
def get_all_scholarships(category: Optional[str] = None, limit: int = 100):
    """
    Get all available scholarships, optionally filtered by category
    """
    scholarships = []
    
    for s in SCHOLARSHIPS_DATABASE:
        # Filter by category if specified
        if category and s.get("category") != category:
            continue
        
        scholarships.append({
            "id": s["id"],
            "title": s["title"],
            "provider": s["provider"],
            "amount": s["amount"],
            "deadline": s["deadline"],
            "category": s["category"],
            "criteria": s["criteria"],
            "tags": s.get("tags", [])
        })
        
        if len(scholarships) >= limit:
            break
    
    return {
        "success": True,
        "count": len(scholarships),
        "scholarships": scholarships
    }


@app.get("/api/scholarships/search")
def search_scholarships(q: str, limit: int = 20):
    """
    Search scholarships by keyword in title, provider, criteria, or tags
    """
    query = q.lower()
    results = []
    
    for s in SCHOLARSHIPS_DATABASE:
        # Search in multiple fields
        searchable = f"{s['title']} {s['provider']} {s['criteria']} {' '.join(s.get('tags', []))}".lower()
        
        if query in searchable:
            results.append({
                "id": s["id"],
                "title": s["title"],
                "provider": s["provider"],
                "amount": s["amount"],
                "deadline": s["deadline"],
                "category": s["category"],
                "criteria": s["criteria"],
                "tags": s.get("tags", [])
            })
            
            if len(results) >= limit:
                break
    
    return {
        "success": True,
        "query": q,
        "count": len(results),
        "scholarships": results
    }


@app.get("/api/scholarships/{scholarship_id}")
def get_scholarship_details(scholarship_id: str):
    """
    Get detailed information about a specific scholarship
    """
    scholarship = get_scholarship_by_id(scholarship_id)
    
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    
    return {
        "success": True,
        "data": {
            "id": scholarship["id"],
            "title": scholarship["title"],
            "provider": scholarship["provider"],
            "amount": scholarship["amount"],
            "deadline": scholarship["deadline"],
            "category": scholarship["category"],
            "criteria": scholarship["criteria"],
            "tags": scholarship.get("tags", []),
            "rules": scholarship.get("rules", {})
        }
    }


@app.get("/api/scholarships/recommend/{student_id}")
def recommend_scholarships(student_id: str, min_score: float = 50):
    """
    Get scholarship recommendations for a student based on their profile
    """
    # Get student data from Firebase or in-memory
    if USE_FIREBASE:
        student_data = fb_get_student(student_id)
        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found. Register student first via POST /api/students/register")
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found. Register student first via POST /api/students/register")
        student_data = students_db[student_id]
    
    try:
        student = StudentProfile(**student_data)
        
        # Find matching scholarships
        matches = find_matching_scholarships(student, min_score)
        
        # Convert to dict for response
        recommendations = []
        for match in matches:
            recommendations.append(match.model_dump(by_alias=True))
        
        return {
            "success": True,
            "studentId": student_id,
            "studentName": student.name,
            "count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.post("/api/scholarships/recommend-direct")
def recommend_scholarships_direct(profile: StudentProfile, min_score: float = 50):
    """
    Get scholarship recommendations directly from profile data (no registration needed)
    
    Example body:
    {
        "name": "Test Student",
        "region": "Karnataka", 
        "overallPercentage": 85.5,
        "incomeLevel": "< 2 LPA",
        "category": "SC"
    }
    """
    try:
        # Find matching scholarships
        matches = find_matching_scholarships(profile, min_score)
        
        # Convert to dict for response
        recommendations = []
        for match in matches:
            recommendations.append({
                "id": match.id,
                "title": match.title,
                "provider": match.provider,
                "amount": match.amount,
                "deadline": match.deadline,
                "category": match.category,
                "criteria": match.criteria,
                "tags": match.tags,
                "matchScore": match.match_score,
                "reason": match.reason,
                "autofillStatement": match.autofill_statement
            })
        
        return {
            "success": True,
            "studentName": profile.name,
            "count": len(recommendations),
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


# ==================== APPLICATION APIs ====================

@app.post("/api/applications/apply")
def apply_scholarship(student_id: str, scholarship_id: str):
    """
    Apply for a scholarship (stored in Firebase if available)
    """
    # Validate student exists
    if USE_FIREBASE:
        student = fb_get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found")
        student = students_db[student_id]
    
    # Validate scholarship exists
    scholarship = get_scholarship_by_id(scholarship_id)
    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    
    # Check if already applied
    if USE_FIREBASE:
        existing_apps = fb_list_applications(student_id=student_id)
        for app in existing_apps:
            if app.get("scholarshipId") == scholarship_id:
                raise HTTPException(status_code=400, detail="Already applied for this scholarship")
    else:
        for app in applications_db.values():
            if app["studentId"] == student_id and app["scholarshipId"] == scholarship_id:
                raise HTTPException(status_code=400, detail="Already applied for this scholarship")
    
    # Create application
    now = datetime.utcnow().isoformat()
    
    application = {
        "studentId": student_id,
        "studentName": student.get("name", "Unknown"),
        "scholarshipId": scholarship_id,
        "scholarshipName": scholarship["title"],
        "category": scholarship["category"],
        "appliedAt": now,
        "status": ApplicationStatus.PENDING.value,
        "updatedAt": now
    }
    
    if USE_FIREBASE:
        application_id = fb_create_application(application)
        if not application_id:
            raise HTTPException(status_code=500, detail="Failed to save application to Firebase")
    else:
        application_id = str(uuid.uuid4())
        application["id"] = application_id
        applications_db[application_id] = application
    
    application["id"] = application_id
    
    return {
        "success": True,
        "message": "Application submitted successfully",
        "applicationId": application_id,
        "storage": "Firebase" if USE_FIREBASE else "In-memory",
        "data": application
    }


@app.get("/api/applications/status/{application_id}")
def get_application_status(application_id: str):
    """
    Get status of a scholarship application
    """
    if USE_FIREBASE:
        app_data = fb_get_application(application_id)
        if not app_data:
            raise HTTPException(status_code=404, detail="Application not found")
    else:
        if application_id not in applications_db:
            raise HTTPException(status_code=404, detail="Application not found")
        app_data = applications_db[application_id]
    
    return {
        "success": True,
        "data": app_data
    }


@app.get("/api/applications/student/{student_id}")
def get_student_applications(student_id: str):
    """
    Get all applications for a student
    """
    # Validate student exists
    if USE_FIREBASE:
        student = fb_get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student_apps = fb_list_applications(student_id=student_id)
    else:
        if student_id not in students_db:
            raise HTTPException(status_code=404, detail="Student not found")
        student_apps = [
            app for app in applications_db.values() 
            if app["studentId"] == student_id
        ]
    
    return {
        "success": True,
        "studentId": student_id,
        "count": len(student_apps),
        "applications": student_apps
    }


@app.put("/api/applications/{application_id}/withdraw")
def withdraw_application(application_id: str):
    """
    Withdraw/cancel a scholarship application
    """
    if USE_FIREBASE:
        app_data = fb_get_application(application_id)
        if not app_data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Can only withdraw pending applications
        if app_data["status"] != ApplicationStatus.PENDING.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot withdraw application with status: {app_data['status']}"
            )
        
        # Update status
        updates = {
            "status": "Withdrawn",
            "updatedAt": datetime.utcnow().isoformat()
        }
        fb_update_application(application_id, updates)
        app_data.update(updates)
    else:
        if application_id not in applications_db:
            raise HTTPException(status_code=404, detail="Application not found")
        
        app_data = applications_db[application_id]
        
        # Can only withdraw pending applications
        if app_data["status"] != ApplicationStatus.PENDING.value:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot withdraw application with status: {app_data['status']}"
            )
        
        # Update status
        app_data["status"] = "Withdrawn"
        app_data["updatedAt"] = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "message": "Application withdrawn successfully",
        "data": app_data
    }


@app.get("/api/applications")
def get_all_applications(status: Optional[str] = None, limit: int = 100):
    """
    Get all applications, optionally filtered by status
    """
    if USE_FIREBASE:
        all_apps = fb_list_applications(limit=limit)
        if status:
            all_apps = [app for app in all_apps if app.get("status") == status]
    else:
        all_apps = []
        for app in applications_db.values():
            if status and app["status"] != status:
                continue
            all_apps.append(app)
            if len(all_apps) >= limit:
                break
    
    return {
        "success": True,
        "count": len(all_apps),
        "storage": "Firebase" if USE_FIREBASE else "In-memory",
        "applications": all_apps
    }


# ==================== STATS API ====================

@app.get("/api/stats")
def get_stats():
    """
    Get system statistics
    """
    if USE_FIREBASE:
        students = fb_list_students()
        applications = fb_list_applications()
        
        return {
            "success": True,
            "storage": "Firebase",
            "stats": {
                "totalStudents": len(students),
                "totalScholarships": len(SCHOLARSHIPS_DATABASE),
                "totalApplications": len(applications),
                "applicationsByStatus": {
                    "Pending": sum(1 for a in applications if a.get("status") == "Pending"),
                    "Approved": sum(1 for a in applications if a.get("status") == "Approved"),
                    "Rejected": sum(1 for a in applications if a.get("status") == "Rejected"),
                    "Withdrawn": sum(1 for a in applications if a.get("status") == "Withdrawn")
                }
            }
        }
    else:
        return {
            "success": True,
            "storage": "In-memory",
            "stats": {
                "totalStudents": len(students_db),
                "totalScholarships": len(SCHOLARSHIPS_DATABASE),
                "totalApplications": len(applications_db),
                "applicationsByStatus": {
                    "Pending": sum(1 for a in applications_db.values() if a["status"] == "Pending"),
                    "Approved": sum(1 for a in applications_db.values() if a["status"] == "Approved"),
                    "Rejected": sum(1 for a in applications_db.values() if a["status"] == "Rejected"),
                    "Withdrawn": sum(1 for a in applications_db.values() if a["status"] == "Withdrawn")
                }
            }
        }


# ==================== FIREBASE TEST APIs ====================

@app.get("/api/firebase/status")
def firebase_status():
    """Check Firebase connection status"""
    return {
        "firebaseAvailable": FIREBASE_AVAILABLE,
        "firebaseEnabled": USE_FIREBASE,
        "message": "Firebase ENABLED - data persists!" if USE_FIREBASE else "In-memory mode - data clears on restart"
    }


@app.post("/api/firebase/test-write")
def test_firebase_write():
    """
    Test Firebase write operation - creates a test document
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Firebase not available")
    
    # Initialize Firebase (requires credentials)
    if not initialize_firebase():
        raise HTTPException(
            status_code=503, 
            detail="Firebase initialization failed. Set FIREBASE_CREDENTIALS env var to path of service account JSON"
        )
    
    # Test data
    test_data = {
        "name": "Test Student",
        "region": "Test Region",
        "overallPercentage": 85.5,
        "incomeLevel": "< 2 LPA",
        "testTimestamp": datetime.utcnow().isoformat()
    }
    
    # Write to Firebase
    doc_id = fb_create_student(test_data)
    
    if doc_id:
        return {
            "success": True,
            "message": "Test write successful!",
            "documentId": doc_id,
            "data": test_data
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to write to Firebase")


@app.get("/api/firebase/test-read/{doc_id}")
def test_firebase_read(doc_id: str):
    """
    Test Firebase read operation - reads a document by ID
    """
    if not FIREBASE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Firebase not available")
    
    if not initialize_firebase():
        raise HTTPException(
            status_code=503, 
            detail="Firebase initialization failed"
        )
    
    # Read from Firebase
    student_data = fb_get_student(doc_id)
    
    if student_data:
        return {
            "success": True,
            "message": "Test read successful!",
            "documentId": doc_id,
            "data": student_data
        }
    else:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")


# ==================== DATA NORMALIZATION APIs ====================

from services.normalization_service import (
    normalize_to_percentage,
    normalize_income,
    normalize_student_profile,
    cgpa_to_percentage_cbse,
    gpa4_to_percentage,
    letter_grade_to_percentage,
    generate_conversion_table
)


@app.post("/api/normalize/score")
def normalize_score(
    score: float,
    score_type: Optional[str] = None,
    university: Optional[str] = None
):
    """
    Normalize any academic score to percentage
    
    - **score**: The score value (CGPA, GPA, or percentage)
    - **score_type**: Type hint ('cgpa', 'gpa', 'grade', 'percentage')
    - **university**: University name for specific formula (optional)
    
    Returns normalized percentage and equivalents in other scales
    """
    result = normalize_to_percentage(score, score_type, university)
    return {
        "success": True,
        "data": result
    }


@app.post("/api/normalize/grade")
def normalize_grade(grade: str):
    """
    Convert letter grade to percentage and other scales
    
    - **grade**: Letter grade (O, A+, A, B+, B, C+, C, D, F)
    """
    result = normalize_to_percentage(grade, "grade")
    return {
        "success": True,
        "data": result
    }


@app.post("/api/normalize/cgpa")
def normalize_cgpa(cgpa: float, university: Optional[str] = None):
    """
    Convert CGPA (10-point scale) to percentage
    
    - **cgpa**: CGPA value (0-10)
    - **university**: University for specific formula (vtu, mumbai, cbse)
    """
    result = normalize_to_percentage(cgpa, "cgpa", university)
    return {
        "success": True,
        "data": result
    }


@app.post("/api/normalize/gpa")
def normalize_gpa(gpa: float):
    """
    Convert GPA (4.0 scale) to percentage
    
    - **gpa**: GPA value (0-4)
    """
    result = normalize_to_percentage(gpa, "gpa")
    return {
        "success": True,
        "data": result
    }


@app.post("/api/normalize/income")
def normalize_income_endpoint(income: str):
    """
    Normalize income string to annual value and category
    
    - **income**: Income string (e.g., "< 2 LPA", "2,00,000", "2 Lakhs")
    """
    result = normalize_income(income)
    return {
        "success": True,
        "data": result
    }


@app.get("/api/normalize/conversion-table")
def get_conversion_table():
    """
    Get complete CGPA/Percentage/GPA/Grade conversion table
    
    Returns a reference table showing equivalent values across all scales
    """
    table = generate_conversion_table()
    return {
        "success": True,
        "description": "Conversion table: CGPA (10) ↔ Percentage ↔ GPA (4.0) ↔ Letter Grade",
        "formula_used": "CBSE Standard: Percentage = CGPA × 9.5",
        "count": len(table),
        "table": table
    }


@app.post("/api/normalize/student")
def normalize_student_endpoint(profile: StudentProfile):
    """
    Normalize all academic and financial data in a student profile
    
    Converts CGPA to percentage, normalizes income, calculates subject percentages
    """
    profile_dict = profile.model_dump(by_alias=True, exclude_none=True)
    normalized = normalize_student_profile(profile_dict)
    return {
        "success": True,
        "data": normalized
    }


# ==================== EXPLAINABLE DECISION APIs ====================

from services.explainability_service import (
    explain_eligibility,
    explain_all_scholarships
)


@app.post("/api/explain/eligibility")
def explain_scholarship_eligibility(
    profile: StudentProfile,
    scholarship_id: str
):
    """
    Get detailed explanation of why a student is/isn't eligible for a specific scholarship
    
    Shows each criterion checked and whether it passed or failed with detailed reasoning
    """
    # Get scholarship
    scholarship = get_scholarship_by_id(scholarship_id)
    if not scholarship:
        raise HTTPException(status_code=404, detail=f"Scholarship '{scholarship_id}' not found")
    
    # Convert profile to dict
    student_dict = profile.model_dump(by_alias=True, exclude_none=True)
    
    # Generate explanation
    explanation = explain_eligibility(student_dict, scholarship)
    
    return {
        "success": True,
        "data": explanation
    }


@app.post("/api/explain/all-scholarships")
def explain_all_scholarships_eligibility(profile: StudentProfile):
    """
    Get detailed eligibility explanations for ALL scholarships
    
    Returns comprehensive report showing:
    - Which scholarships the student is eligible for
    - Which scholarships they're not eligible for and why
    - Detailed breakdown of each criterion check
    """
    student_dict = profile.model_dump(by_alias=True, exclude_none=True)
    
    # Get all scholarships
    scholarships = SCHOLARSHIPS_DATABASE
    
    # Generate explanations for all
    report = explain_all_scholarships(student_dict, scholarships)
    
    return {
        "success": True,
        "data": report
    }


@app.get("/api/explain/student/{student_id}/scholarship/{scholarship_id}")
def explain_student_scholarship_eligibility(student_id: str, scholarship_id: str):
    """
    Explain eligibility for a specific student and scholarship (using stored student data)
    """
    # Get student
    if USE_FIREBASE:
        student_data = fb_get_student(student_id)
    else:
        student_data = students_db.get(student_id)
    
    if not student_data:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    
    # Get scholarship
    scholarship = get_scholarship_by_id(scholarship_id)
    if not scholarship:
        raise HTTPException(status_code=404, detail=f"Scholarship '{scholarship_id}' not found")
    
    # Generate explanation
    explanation = explain_eligibility(student_data, scholarship)
    
    return {
        "success": True,
        "studentId": student_id,
        "studentName": student_data.get("name"),
        "data": explanation
    }


@app.get("/api/explain/student/{student_id}/all")
def explain_student_all_scholarships(student_id: str):
    """
    Explain eligibility for a specific student against ALL scholarships
    
    Provides a complete eligibility report with detailed explanations
    """
    # Get student
    if USE_FIREBASE:
        student_data = fb_get_student(student_id)
    else:
        student_data = students_db.get(student_id)
    
    if not student_data:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    
    # Generate explanations for all scholarships
    report = explain_all_scholarships(student_data, SCHOLARSHIPS_DATABASE)
    
    return {
        "success": True,
        "studentId": student_id,
        "data": report
    }


# ==================== COMPLETE PIPELINE API ====================
# This demonstrates the full flow: Upload → OCR → AI Extraction → Normalization → Eligibility → Recommendations

from services.gemini_service import parse_marksheet_with_ai

@app.post("/api/pipeline/complete")
async def complete_scholarship_pipeline(
    file: UploadFile = File(...),
    income_level: str = "< 2 LPA",
    region: str = "India"
):
    """
    🚀 COMPLETE SCHOLARSHIP PIPELINE
    
    Single endpoint that processes the entire flow:
    1. ✅ Upload marksheet
    2. ✅ OCR text extraction
    3. ✅ AI-powered data parsing
    4. ✅ Data normalization
    5. ✅ Eligibility matching
    6. ✅ Recommendation ranking
    7. ✅ Explainable results
    
    Returns comprehensive scholarship recommendations with explanations
    """
    import time
    start_time = time.time()
    
    pipeline_results = {
        "success": True,
        "pipeline": "complete",
        "stages": {},
        "timing": {}
    }
    
    try:
        # ========== STAGE 1: FILE UPLOAD ==========
        stage_start = time.time()
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {allowed_types}"
            )
        
        # Save file temporarily
        upload_id = str(uuid.uuid4())
        temp_dir = os.path.join(tempfile.gettempdir(), "scholarship_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_ext = os.path.splitext(file.filename)[1] or ".jpg"
        file_path = os.path.join(temp_dir, f"{upload_id}{file_ext}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        pipeline_results["stages"]["upload"] = {
            "status": "✅ Complete",
            "uploadId": upload_id,
            "fileName": file.filename,
            "fileType": file.content_type
        }
        pipeline_results["timing"]["upload"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 2: OCR EXTRACTION ==========
        stage_start = time.time()
        
        # Preprocess if image
        if file.content_type.startswith("image/"):
            processed_path = preprocess_image(file_path)
        else:
            processed_path = file_path
        
        # Extract text
        extracted_text = extract_text_from_file(processed_path)
        
        pipeline_results["stages"]["ocr"] = {
            "status": "✅ Complete",
            "characterCount": len(extracted_text),
            "preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        }
        pipeline_results["timing"]["ocr"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 3: AI PARSING ==========
        stage_start = time.time()
        
        try:
            # Use AI to extract structured data
            student_profile = await parse_marksheet_with_ai(extracted_text)
            
            # Convert to dict
            student_data = student_profile.model_dump(by_alias=True, exclude_none=True)
            student_data["incomeLevel"] = income_level
            student_data["region"] = region
            
            pipeline_results["stages"]["ai_parsing"] = {
                "status": "✅ Complete",
                "extractedName": student_data.get("name", "Unknown"),
                "extractedPercentage": student_data.get("overallPercentage", 0),
                "subjectsFound": len(student_data.get("marks", []))
            }
        except Exception as e:
            # Fallback to manual data if AI fails
            student_data = {
                "name": "Student (Manual Entry Required)",
                "overallPercentage": 0,
                "incomeLevel": income_level,
                "region": region,
                "marks": [],
                "extractedFromDoc": False
            }
            pipeline_results["stages"]["ai_parsing"] = {
                "status": "⚠️ Partial (AI extraction failed)",
                "error": str(e),
                "fallback": "Manual entry required"
            }
        
        pipeline_results["timing"]["ai_parsing"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 4: DATA NORMALIZATION ==========
        stage_start = time.time()
        
        normalized_data = normalize_student_profile(student_data)
        
        pipeline_results["stages"]["normalization"] = {
            "status": "✅ Complete",
            "normalizedPercentage": normalized_data.get("overallPercentage", 0),
            "incomeCategory": normalized_data.get("normalizedIncome", {}).get("income_category", "Unknown")
        }
        pipeline_results["timing"]["normalization"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 5: ELIGIBILITY MATCHING ==========
        stage_start = time.time()
        
        # Get matching scholarships
        matching_scholarships = find_matching_scholarships(normalized_data)
        
        pipeline_results["stages"]["eligibility"] = {
            "status": "✅ Complete",
            "totalScholarships": len(SCHOLARSHIPS_DATABASE),
            "eligibleCount": len(matching_scholarships)
        }
        pipeline_results["timing"]["eligibility"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 6: RECOMMENDATION RANKING ==========
        stage_start = time.time()
        
        # Sort by match score
        ranked_scholarships = sorted(
            matching_scholarships,
            key=lambda x: x.get("matchScore", 0),
            reverse=True
        )
        
        # Get top recommendations
        top_recommendations = ranked_scholarships[:5]
        
        pipeline_results["stages"]["ranking"] = {
            "status": "✅ Complete",
            "topRecommendations": len(top_recommendations)
        }
        pipeline_results["timing"]["ranking"] = round(time.time() - stage_start, 3)
        
        # ========== STAGE 7: GENERATE EXPLANATIONS ==========
        stage_start = time.time()
        
        # Generate explanations for top scholarships
        explanations = []
        for scholarship in top_recommendations[:3]:
            # Find full scholarship data
            full_scholarship = get_scholarship_by_id(scholarship["id"])
            if full_scholarship:
                explanation = explain_eligibility(normalized_data, full_scholarship)
                explanations.append({
                    "scholarshipId": scholarship["id"],
                    "title": scholarship["title"],
                    "matchScore": scholarship.get("matchScore", 0),
                    "explanation": explanation
                })
        
        pipeline_results["stages"]["explanations"] = {
            "status": "✅ Complete",
            "explanationsGenerated": len(explanations)
        }
        pipeline_results["timing"]["explanations"] = round(time.time() - stage_start, 3)
        
        # ========== COMPILE FINAL RESULTS ==========
        pipeline_results["timing"]["total"] = round(time.time() - start_time, 3)
        
        pipeline_results["student"] = {
            "name": normalized_data.get("name"),
            "percentage": normalized_data.get("overallPercentage"),
            "category": normalized_data.get("category"),
            "incomeLevel": normalized_data.get("incomeLevel"),
            "region": normalized_data.get("region"),
            "marks": normalized_data.get("marks", [])[:5]  # First 5 subjects
        }
        
        pipeline_results["recommendations"] = {
            "total": len(ranked_scholarships),
            "top5": [
                {
                    "id": s["id"],
                    "title": s["title"],
                    "provider": s.get("provider", ""),
                    "amount": s.get("amount", ""),
                    "matchScore": s.get("matchScore", 0),
                    "reason": s.get("reason", "")
                }
                for s in top_recommendations
            ]
        }
        
        pipeline_results["explanations"] = explanations
        
        # Cleanup temp file
        try:
            os.remove(file_path)
            if processed_path != file_path:
                os.remove(processed_path)
        except:
            pass
        
        return pipeline_results
        
    except HTTPException:
        raise
    except Exception as e:
        pipeline_results["success"] = False
        pipeline_results["error"] = str(e)
        pipeline_results["timing"]["total"] = round(time.time() - start_time, 3)
        return pipeline_results


@app.get("/api/pipeline/status")
def get_pipeline_status():
    """
    Get the status of all pipeline components
    
    Shows which services are available and configured
    """
    from services.gemini_service import GEMINI_API_KEY
    from services.ocr_service import TESSERACT_AVAILABLE, PDF2IMAGE_AVAILABLE
    
    return {
        "success": True,
        "pipeline": {
            "name": "AI Scholarship Eligibility Pipeline",
            "version": "1.0.0",
            "description": "Complete flow from marksheet upload to scholarship recommendations"
        },
        "components": {
            "authentication": {
                "status": "✅ Active",
                "features": ["Login", "Register", "JWT Tokens", "Role-based Access"]
            },
            "marksheet_upload": {
                "status": "✅ Active",
                "supportedFormats": ["JPEG", "PNG", "PDF"]
            },
            "ocr_extraction": {
                "status": "✅ Active" if TESSERACT_AVAILABLE else "⚠️ AI Fallback",
                "tesseract": "Available" if TESSERACT_AVAILABLE else "Not Installed",
                "pdf_support": "Available" if PDF2IMAGE_AVAILABLE else "Limited"
            },
            "ai_parsing": {
                "status": "✅ Active" if GEMINI_API_KEY else "❌ Not Configured",
                "model": "Gemini 2.0 Flash",
                "apiConfigured": bool(GEMINI_API_KEY)
            },
            "data_normalization": {
                "status": "✅ Active",
                "features": ["CGPA→%", "GPA→%", "Grade→%", "Income Parsing"]
            },
            "eligibility_engine": {
                "status": "✅ Active",
                "totalScholarships": len(SCHOLARSHIPS_DATABASE),
                "criteria": ["Category", "Income", "Marks", "Region", "Gender", "Age"]
            },
            "recommendation_ranking": {
                "status": "✅ Active",
                "algorithm": "Multi-factor scoring"
            },
            "explainability": {
                "status": "✅ Active",
                "features": ["Detailed reasons", "Pass/Fail breakdown", "Suggestions"]
            },
            "database": {
                "status": "✅ Firebase" if USE_FIREBASE else "⚠️ In-Memory",
                "persistent": USE_FIREBASE
            }
        },
        "flow": [
            "1️⃣ Frontend → Backend Server",
            "2️⃣ → Authentication Check",
            "3️⃣ → Marksheet Upload",
            "4️⃣ → AI OCR Processing",
            "5️⃣ → Data Normalization",
            "6️⃣ → Eligibility Matching",
            "7️⃣ → Recommendation Ranking",
            "8️⃣ → Results Sent to Frontend"
        ]
    }
