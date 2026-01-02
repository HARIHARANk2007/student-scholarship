"""
FastAPI Routes for Scholarship Operations
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from models.types import Scholarship
# from database.firebase_service import get_firebase_service
from services.scholarship_recommendation_engine import SCHOLARSHIPS_DATABASE, get_scholarship_by_id

router = APIRouter(prefix="/api/scholarships", tags=["scholarships"])


@router.get("/", response_model=List[Scholarship])
async def list_scholarships(category: Optional[str] = None, limit: int = 100):
    """
    List all scholarships from the database
    Optionally filter by category
    """
    try:
        scholarships = []
        for s in SCHOLARSHIPS_DATABASE:
            if category and s.get("category") != category:
                continue
            
            scholarship = Scholarship(
                id=s["id"],
                title=s["title"],
                provider=s["provider"],
                amount=s["amount"],
                deadline=s["deadline"],
                category=s["category"],
                criteria=s["criteria"],
                tags=s["tags"],
                apply_url=s.get("applyUrl")
            )
            scholarships.append(scholarship)
            
            if len(scholarships) >= limit:
                break
        
        return scholarships
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{scholarship_id}", response_model=Scholarship)
async def get_scholarship(scholarship_id: str):
    """Get scholarship details by ID"""
    try:
        scholarship_data = get_scholarship_by_id(scholarship_id)
        
        if not scholarship_data:
            raise HTTPException(status_code=404, detail="Scholarship not found")
        
        return Scholarship(
            id=scholarship_data["id"],
            title=scholarship_data["title"],
            provider=scholarship_data["provider"],
            amount=scholarship_data["amount"],
            deadline=scholarship_data["deadline"],
            category=scholarship_data["category"],
            criteria=scholarship_data["criteria"],
            tags=scholarship_data["tags"],
            apply_url=scholarship_data.get("applyUrl")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/list", response_model=List[str])
async def list_categories():
    """Get list of all scholarship categories"""
    try:
        categories = set()
        for s in SCHOLARSHIPS_DATABASE:
            categories.add(s["category"])
        return sorted(list(categories))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tags/list", response_model=List[str])
async def list_tags():
    """Get list of all scholarship tags"""
    try:
        tags = set()
        for s in SCHOLARSHIPS_DATABASE:
            tags.update(s["tags"])
        return sorted(list(tags))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
