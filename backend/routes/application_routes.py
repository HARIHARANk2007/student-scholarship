"""
FastAPI Routes for Application Operations
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.types import StudentApplication, ApplicationStatus
# from database.firebase_service import get_firebase_service
from datetime import datetime

router = APIRouter(prefix="/api/applications", tags=["applications"])


def get_firebase():
    return get_firebase_service()


@router.post("/", response_model=dict)
async def create_application(application: StudentApplication):
    """Create a new scholarship application"""
    try:
        firebase = get_firebase()
        application_data = application.model_dump(by_alias=True, exclude_none=True)
        
        # Set default values
        if "appliedAt" not in application_data:
            application_data["appliedAt"] = datetime.utcnow().isoformat()
        if "status" not in application_data:
            application_data["status"] = ApplicationStatus.PENDING.value
        
        application_id = firebase.create_application(application_data)
        return {"success": True, "id": application_id, "message": "Application created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{application_id}", response_model=StudentApplication)
async def get_application(application_id: str):
    """Get application by ID"""
    try:
        firebase = get_firebase()
        application_data = firebase.get_application(application_id)
        if not application_data:
            raise HTTPException(status_code=404, detail="Application not found")
        return StudentApplication(**application_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{application_id}", response_model=dict)
async def update_application(application_id: str, updates: dict):
    """Update application"""
    try:
        firebase = get_firebase()
        success = firebase.update_application(application_id, updates)
        return {"success": success, "message": "Application updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[StudentApplication])
async def list_applications(student_id: Optional[str] = None, limit: int = 100):
    """List applications, optionally filtered by student"""
    try:
        firebase = get_firebase()
        applications_data = firebase.list_applications(student_id, limit)
        return [StudentApplication(**app) for app in applications_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{application_id}/status", response_model=dict)
async def update_application_status(application_id: str, status: ApplicationStatus):
    """Update application status"""
    try:
        firebase = get_firebase()
        success = firebase.update_application(application_id, {"status": status.value})
        return {"success": success, "message": f"Application status updated to {status.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/student/{student_id}", response_model=List[StudentApplication])
async def get_student_applications(student_id: str):
    """Get all applications for a specific student"""
    try:
        firebase = get_firebase()
        applications_data = firebase.list_applications(student_id=student_id)
        return [StudentApplication(**app) for app in applications_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
