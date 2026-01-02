# Routes package
from .student_routes import router as student_router
from .scholarship_routes import router as scholarship_router
from .application_routes import router as application_router

__all__ = [
    "student_router",
    "scholarship_router",
    "application_router"
]
