"""
Test script for Student Scholarship APIs using FastAPI TestClient
This runs tests directly without needing a separate server process
"""

from fastapi.testclient import TestClient
import json
import time

# Import the FastAPI app
from main import app

client = TestClient(app)

def test_api(name, method, url, data=None, headers=None):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = client.get(url, headers=headers)
        elif method == "POST":
            response = client.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = client.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = client.delete(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        try:
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)[:500]}")
            return result
        except:
            print(f"   Response: {response.text[:500]}")
            return None
    except Exception as e:
        print(f"   ERROR: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("STUDENT SCHOLARSHIP API TESTS - COMPLETE")
    print("="*60)
    
    # ===== HEALTH & STATUS =====
    test_api("Health Check", "GET", "/")
    test_api("Students Test", "GET", "/api/students/test")
    test_api("System Stats", "GET", "/api/stats")
    
    # ===== AUTHENTICATION APIs =====
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS")
    print("="*60)
    
    # Register a new student user
    register_data = {
        "email": f"student_{int(time.time())}@test.com",
        "password": "password123",
        "name": "Test Student",
        "role": "student"
    }
    result = test_api("Register Student User", "POST", "/api/auth/register", register_data)
    student_token = result.get("accessToken") if result else None
    
    # Login as admin
    admin_login = {
        "email": "admin@scholarship.com",
        "password": "admin123"
    }
    result = test_api("Admin Login", "POST", "/api/auth/login", admin_login)
    admin_token = result.get("accessToken") if result else None
    
    # Get current user with token
    if student_token:
        headers = {"Authorization": f"Bearer {student_token}"}
        test_api("Get Current User (Student)", "GET", "/api/auth/me", headers=headers)
    
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_api("Get Current User (Admin)", "GET", "/api/auth/me", headers=headers)
        test_api("List All Users (Admin)", "GET", "/api/auth/users", headers=headers)
    
    # Verify token
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_api("Verify Token", "GET", "/api/auth/verify", headers=headers)
    
    # Test role-based access (student trying admin route)
    if student_token:
        headers = {"Authorization": f"Bearer {student_token}"}
        test_api("Student Access Admin Route (Should Fail)", "GET", "/api/auth/users", headers=headers)
    
    # Test invalid login
    bad_login = {"email": "admin@scholarship.com", "password": "wrongpass"}
    test_api("Invalid Login (Wrong Password)", "POST", "/api/auth/login", bad_login)
    
    # ===== STUDENT APIs =====
    print("\n" + "="*60)
    print("STUDENT TESTS")
    print("="*60)
    
    student_data = {
        "name": "Rahul Kumar",
        "region": "Karnataka",
        "overallPercentage": 85.5,
        "incomeLevel": "< 2 LPA",
        "category": "SC"
    }
    result = test_api("Register Student", "POST", "/api/students/register", student_data)
    student_id = result.get("studentId") if result else None
    
    if student_id:
        test_api("Get Student Profile", "GET", f"/api/students/{student_id}")
        
        # Update student
        updated_data = {
            "name": "Rahul Kumar Updated",
            "region": "Karnataka",
            "overallPercentage": 90.0,
            "incomeLevel": "< 2 LPA",
            "category": "SC"
        }
        test_api("Update Student", "PUT", f"/api/students/{student_id}", updated_data)
    
    test_api("Get All Students", "GET", "/api/students")
    
    # ===== SCHOLARSHIP APIs =====
    test_api("Get All Scholarships", "GET", "/api/scholarships")
    test_api("Search Scholarships", "GET", "/api/scholarships/search?q=SC")
    test_api("Get Scholarship Details", "GET", "/api/scholarships/sc-post-matric")
    
    # Direct Recommendations
    recommend_data = {
        "name": "Priya Singh",
        "region": "Tamil Nadu",
        "overallPercentage": 92.0,
        "incomeLevel": "< 2 LPA",
        "category": "SC",
        "isFirstGraduate": True
    }
    test_api("Direct Recommendations", "POST", "/api/scholarships/recommend-direct", recommend_data)
    
    if student_id:
        test_api("Recommendations for Student", "GET", f"/api/scholarships/recommend/{student_id}")
    
    # ===== APPLICATION APIs =====
    if student_id:
        # Apply for scholarship
        apply_url = f"/api/applications/apply?student_id={student_id}&scholarship_id=sc-post-matric"
        result = test_api("Apply for Scholarship", "POST", apply_url)
        app_id = result.get("applicationId") if result else None
        
        if app_id:
            test_api("Get Application Status", "GET", f"/api/applications/status/{app_id}")
            test_api("Withdraw Application", "PUT", f"/api/applications/{app_id}/withdraw")
        
        test_api("Get Student Applications", "GET", f"/api/applications/student/{student_id}")
    
    test_api("Get All Applications", "GET", "/api/applications")
    
    # ===== FIREBASE =====
    test_api("Firebase Status", "GET", "/api/firebase/status")
    
    # ===== FINAL STATS =====
    test_api("Final Stats", "GET", "/api/stats")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    main()
