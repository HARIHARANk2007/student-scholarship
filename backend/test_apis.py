"""
Test script for Student Scholarship APIs
Run with: python test_apis.py
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api(name, method, url, data=None, headers=None):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"   {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)[:500]}")
        return result
    except Exception as e:
        print(f"   [ERROR] Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("STUDENT SCHOLARSHIP API TESTS - COMPLETE")
    print("="*60)
    
    # ===== HEALTH & STATUS =====
    test_api("Health Check", "GET", f"{BASE_URL}/")
    test_api("Students Test", "GET", f"{BASE_URL}/api/students/test")
    test_api("System Stats", "GET", f"{BASE_URL}/api/stats")
    
    # ===== AUTHENTICATION APIs =====
    print("\n" + "="*60)
    print("AUTHENTICATION TESTS")
    print("="*60)
    
    # Register a new student user
    register_data = {
        "email": f"student_{int(__import__('time').time())}@test.com",
        "password": "password123",
        "name": "Test Student",
        "role": "student"
    }
    result = test_api("Register Student User", "POST", f"{BASE_URL}/api/auth/register", register_data)
    student_token = result.get("accessToken") if result else None
    
    # Login as admin
    admin_login = {
        "email": "admin@scholarship.com",
        "password": "admin123"
    }
    result = test_api("Admin Login", "POST", f"{BASE_URL}/api/auth/login", admin_login)
    admin_token = result.get("accessToken") if result else None
    
    # Get current user with token
    if student_token:
        headers = {"Authorization": f"Bearer {student_token}"}
        test_api("Get Current User (Student)", "GET", f"{BASE_URL}/api/auth/me", headers=headers)
    
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_api("Get Current User (Admin)", "GET", f"{BASE_URL}/api/auth/me", headers=headers)
        test_api("List All Users (Admin)", "GET", f"{BASE_URL}/api/auth/users", headers=headers)
    
    # Verify token
    if admin_token:
        headers = {"Authorization": f"Bearer {admin_token}"}
        test_api("Verify Token", "GET", f"{BASE_URL}/api/auth/verify", headers=headers)
    
    # Test role-based access (student trying admin route)
    if student_token:
        headers = {"Authorization": f"Bearer {student_token}"}
        test_api("Student Access Admin Route (Should Fail)", "GET", f"{BASE_URL}/api/auth/users", headers=headers)
    
    # Test invalid login
    bad_login = {"email": "admin@scholarship.com", "password": "wrongpass"}
    test_api("Invalid Login (Wrong Password)", "POST", f"{BASE_URL}/api/auth/login", bad_login)
    
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
    result = test_api("Register Student", "POST", f"{BASE_URL}/api/students/register", student_data)
    student_id = result.get("studentId") if result else None
    
    if student_id:
        test_api("Get Student Profile", "GET", f"{BASE_URL}/api/students/{student_id}")
        
        # Update student
        updated_data = {
            "name": "Rahul Kumar Updated",
            "region": "Karnataka",
            "overallPercentage": 90.0,
            "incomeLevel": "< 2 LPA",
            "category": "SC"
        }
        test_api("Update Student", "PUT", f"{BASE_URL}/api/students/{student_id}", updated_data)
    
    test_api("Get All Students", "GET", f"{BASE_URL}/api/students")
    
    # ===== SCHOLARSHIP APIs =====
    test_api("Get All Scholarships", "GET", f"{BASE_URL}/api/scholarships")
    test_api("Search Scholarships", "GET", f"{BASE_URL}/api/scholarships/search?q=SC")
    test_api("Get Scholarship Details", "GET", f"{BASE_URL}/api/scholarships/sc-post-matric")
    
    # Direct Recommendations
    recommend_data = {
        "name": "Priya Singh",
        "region": "Tamil Nadu",
        "overallPercentage": 92.0,
        "incomeLevel": "< 2 LPA",
        "category": "SC",
        "isFirstGraduate": True
    }
    test_api("Direct Recommendations", "POST", f"{BASE_URL}/api/scholarships/recommend-direct", recommend_data)
    
    if student_id:
        test_api("Recommendations for Student", "GET", f"{BASE_URL}/api/scholarships/recommend/{student_id}")
    
    # ===== APPLICATION APIs =====
    if student_id:
        # Apply for scholarship
        apply_url = f"{BASE_URL}/api/applications/apply?student_id={student_id}&scholarship_id=sc-post-matric"
        result = test_api("Apply for Scholarship", "POST", apply_url)
        app_id = result.get("applicationId") if result else None
        
        if app_id:
            test_api("Get Application Status", "GET", f"{BASE_URL}/api/applications/status/{app_id}")
            test_api("Withdraw Application", "PUT", f"{BASE_URL}/api/applications/{app_id}/withdraw")
        
        test_api("Get Student Applications", "GET", f"{BASE_URL}/api/applications/student/{student_id}")
    
    test_api("Get All Applications", "GET", f"{BASE_URL}/api/applications")
    
    # ===== FIREBASE =====
    test_api("Firebase Status", "GET", f"{BASE_URL}/api/firebase/status")
    
    # ===== FINAL STATS =====
    test_api("Final Stats", "GET", f"{BASE_URL}/api/stats")
    
    # ===== CLEANUP (optional) =====
    # if student_id:
    #     test_api("Delete Student", "DELETE", f"{BASE_URL}/api/students/{student_id}")
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    main()
