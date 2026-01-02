"""
Firebase Service for Student Scholarship Application
Handles all Firebase Firestore operations
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# Try importing firebase_admin
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("[WARN] firebase-admin not installed. Run: pip install firebase-admin")


# Global Firebase app instance
_firebase_app = None
_firestore_client = None


def initialize_firebase(credential_path: Optional[str] = None) -> bool:
    """
    Initialize Firebase Admin SDK
    
    Args:
        credential_path: Path to service account JSON file
                        If None, looks for FIREBASE_CREDENTIALS env var
    
    Returns:
        True if initialized successfully, False otherwise
    """
    global _firebase_app, _firestore_client
    
    if not FIREBASE_AVAILABLE:
        print("[ERROR] Firebase Admin SDK not available")
        return False
    
    if _firebase_app is not None:
        print("[OK] Firebase already initialized")
        return True
    
    try:
        # Get credentials path
        cred_path = credential_path or os.environ.get("FIREBASE_CREDENTIALS")
        
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            print(f"[OK] Firebase initialized with credentials from: {cred_path}")
        else:
            # Try default credentials (for Cloud environments)
            _firebase_app = firebase_admin.initialize_app()
            print("[OK] Firebase initialized with default credentials")
        
        _firestore_client = firestore.client()
        return True
        
    except Exception as e:
        print(f"[ERROR] Firebase initialization failed: {e}")
        return False


def get_firestore_client():
    """Get Firestore client, initializing if needed"""
    global _firestore_client
    
    if _firestore_client is None:
        if not initialize_firebase():
            return None
    
    return _firestore_client


# ==================== STUDENT OPERATIONS ====================

def create_student(student_data: Dict[str, Any]) -> Optional[str]:
    """
    Create a new student document in Firestore
    
    Args:
        student_data: Student profile data
        
    Returns:
        Document ID if successful, None otherwise
    """
    db = get_firestore_client()
    if db is None:
        return None
    
    try:
        # Add timestamps
        student_data["createdAt"] = datetime.utcnow().isoformat()
        student_data["updatedAt"] = datetime.utcnow().isoformat()
        
        # Create document
        doc_ref = db.collection("students").add(student_data)
        student_id = doc_ref[1].id
        
        print(f"[OK] Student created with ID: {student_id}")
        return student_id
        
    except Exception as e:
        print(f"[ERROR] Error creating student: {e}")
        return None


def get_student(student_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a student document by ID
    
    Args:
        student_id: Document ID
        
    Returns:
        Student data dict if found, None otherwise
    """
    db = get_firestore_client()
    if db is None:
        return None
    
    try:
        doc = db.collection("students").document(student_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            print(f"[OK] Student found: {student_id}")
            return data
        else:
            print(f"[WARN] Student not found: {student_id}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Error getting student: {e}")
        return None


def update_student(student_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update a student document
    
    Args:
        student_id: Document ID
        updates: Fields to update
        
    Returns:
        True if successful, False otherwise
    """
    db = get_firestore_client()
    if db is None:
        return False
    
    try:
        updates["updatedAt"] = datetime.utcnow().isoformat()
        db.collection("students").document(student_id).update(updates)
        print(f"[OK] Student updated: {student_id}")
        return True
    except Exception as e:
        print(f"[ERROR] Error updating student: {e}")
        return False


def delete_student(student_id: str) -> bool:
    """
    Delete a student document
    
    Args:
        student_id: Document ID
        
    Returns:
        True if successful, False otherwise
    """
    db = get_firestore_client()
    if db is None:
        return False
    
    try:
        db.collection("students").document(student_id).delete()
        print(f"[OK] Student deleted: {student_id}")
        return True
    except Exception as e:
        print(f"[ERROR] Error deleting student: {e}")
        return False


def list_students(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List all students
    
    Args:
        limit: Max results
        offset: Skip results
        
    Returns:
        List of student data dicts
    """
    db = get_firestore_client()
    if db is None:
        return []
    
    try:
        docs = db.collection("students").limit(limit).stream()
        students = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            students.append(data)
        print(f"[OK] Listed {len(students)} students")
        return students
    except Exception as e:
        print(f"[ERROR] Error listing students: {e}")
        return []


# ==================== APPLICATION OPERATIONS ====================

def create_application(application_data: Dict[str, Any]) -> Optional[str]:
    """Create a scholarship application"""
    db = get_firestore_client()
    if db is None:
        return None
    
    try:
        application_data["createdAt"] = datetime.utcnow().isoformat()
        application_data["updatedAt"] = datetime.utcnow().isoformat()
        doc_ref = db.collection("applications").add(application_data)
        app_id = doc_ref[1].id
        print(f"[OK] Application created: {app_id}")
        return app_id
    except Exception as e:
        print(f"[ERROR] Error creating application: {e}")
        return None


def get_application(application_id: str) -> Optional[Dict[str, Any]]:
    """Get application by ID"""
    db = get_firestore_client()
    if db is None:
        return None
    
    try:
        doc = db.collection("applications").document(application_id).get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    except Exception as e:
        print(f"[ERROR] Error getting application: {e}")

def update_application(application_id: str, updates: Dict[str, Any]) -> bool:
    """Update application"""
    db = get_firestore_client()
    if db is None:
        return False
    
    try:
        updates["updatedAt"] = datetime.utcnow().isoformat()
        db.collection("applications").document(application_id).update(updates)
        return True
    except Exception as e:
        print(f"[ERROR] Error updating application: {e}")
        return False


def list_applications(student_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List applications, optionally filtered by student"""
    db = get_firestore_client()
    if db is None:
        return []
    
    try:
        query = db.collection("applications")
        if student_id:
            query = query.where("studentId", "==", student_id)
        
        docs = query.limit(limit).stream()
        applications = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            applications.append(data)
        return applications
    except Exception as e:
        print(f"[ERROR] Error listing applications: {e}")
        return []


def delete_application(application_id: str) -> bool:
    """Delete application"""
    db = get_firestore_client()
    if db is None:
        return False
    
    try:
        db.collection("applications").document(application_id).delete()
        return True
    except Exception as e:
        print(f"[ERROR] Error deleting application: {e}")
        return False


# ==================== TEST FUNCTIONS ====================

def test_firebase_write() -> Dict[str, Any]:
    """
    Test Firebase write operation
    
    Returns:
        Result dict with success status and details
    """
    db = get_firestore_client()
    
    if db is None:
        return {
            "success": False,
            "error": "Firebase not initialized. Check credentials."
        }
    
    try:
        # Write test document
        test_data = {
            "test": True,
            "message": "Firebase connection test",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        doc_ref = db.collection("_test").document("connection_test")
        doc_ref.set(test_data)
        
        print("[OK] Firebase WRITE test passed!")
        return {
            "success": True,
            "operation": "write",
            "collection": "_test",
            "documentId": "connection_test",
            "data": test_data
        }
        
    except Exception as e:
        print(f"[ERROR] Firebase WRITE test failed: {e}")
        return {
            "success": False,
            "operation": "write",
            "error": str(e)
        }


def test_firebase_read() -> Dict[str, Any]:
    """
    Test Firebase read operation
    
    Returns:
        Result dict with success status and details
    """
    db = get_firestore_client()
    
    if db is None:
        return {
            "success": False,
            "error": "Firebase not initialized. Check credentials."
        }
    
    try:
        # Read test document
        doc = db.collection("_test").document("connection_test").get()
        
        if doc.exists:
            data = doc.to_dict()
            print("[OK] Firebase READ test passed!")
            return {
                "success": True,
                "operation": "read",
                "collection": "_test",
                "documentId": "connection_test",
                "data": data
            }
        else:
            return {
                "success": False,
                "operation": "read",
                "error": "Test document not found. Run write test first."
            }
            
    except Exception as e:
        print(f"[ERROR] Firebase READ test failed: {e}")
        return {
            "success": False,
            "operation": "read",
            "error": str(e)
        }


def test_firebase_connection() -> Dict[str, Any]:
    """
    Test both Firebase read and write operations
    
    Returns:
        Combined result of both tests
    """
    write_result = test_firebase_write()
    read_result = test_firebase_read()
    
    all_passed = write_result["success"] and read_result["success"]
    
    return {
        "success": all_passed,
        "message": "Firebase connection OK!" if all_passed else "Firebase test failed",
        "write_test": write_result,
        "read_test": read_result
    }
