# Services package
from .scholarship_recommendation_engine import (
    find_matching_scholarships,
    calculate_match_score,
    get_scholarship_by_id,
    SCHOLARSHIPS_DATABASE
)
from .ocr_service import extract_text_from_file, extract_text_from_image, extract_text_from_pdf

# Lazy import for gemini_service (requires httpx)
# from .gemini_service import parse_marksheet_with_ai, parse_marksheet_with_ai_sync

__all__ = [
    "find_matching_scholarships",
    "calculate_match_score",
    "get_scholarship_by_id",
    "SCHOLARSHIPS_DATABASE",
    "extract_text_from_file",
    "extract_text_from_image",
    "extract_text_from_pdf"
]
