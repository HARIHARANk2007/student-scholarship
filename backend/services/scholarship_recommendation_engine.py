"""
Scholarship Recommendation Engine
Intelligent matching of students with scholarships based on eligibility rules
"""

from typing import List, Dict, Any, Optional
from models.types import StudentProfile, MatchResult, Scholarship
import re


# Define comprehensive scholarship database
SCHOLARSHIPS_DATABASE = [
    # ============ SC/ST/OBC Scholarships ============
    {
        "id": "sc-post-matric",
        "title": "SC Post Matric Scholarship",
        "provider": "Ministry of Social Justice & Empowerment",
        "amount": "₹3,000 - ₹5,000/month",
        "deadline": "Every June 30",
        "category": "SC",
        "criteria": "SC category + Family Income < 2.5 LPA",
        "tags": ["SC", "Post-Matric", "Government"],
        "rules": {
            "category": "SC",
            "maxIncome": 250000,
            "minMarks": 0,
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    {
        "id": "st-post-matric",
        "title": "ST Post Matric Scholarship",
        "provider": "Ministry of Social Justice & Empowerment",
        "amount": "₹3,000 - ₹5,000/month",
        "deadline": "Every June 30",
        "category": "ST",
        "criteria": "ST category + Family Income < 2.5 LPA",
        "tags": ["ST", "Post-Matric", "Government"],
        "rules": {
            "category": "ST",
            "maxIncome": 250000,
            "minMarks": 0,
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    {
        "id": "obc-post-matric",
        "title": "OBC Post Matric Scholarship",
        "provider": "Ministry of Social Justice & Empowerment",
        "amount": "₹2,500 - ₹4,000/month",
        "deadline": "Every June 30",
        "category": "OBC",
        "criteria": "OBC category + Family Income < 2 LPA",
        "tags": ["OBC", "Post-Matric", "Government"],
        "rules": {
            "category": "OBC",
            "maxIncome": 200000,
            "minMarks": 0,
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    # ============ Merit-Based Scholarships ============
    {
        "id": "merit-excellence",
        "title": "Merit Excellence Scholarship",
        "provider": "Department of Education",
        "amount": "₹50,000 - ₹2,00,000/year",
        "deadline": "Every August 15",
        "category": "Merit",
        "criteria": "Marks > 80% + Any category",
        "tags": ["Merit", "National", "Performance"],
        "rules": {
            "minMarks": 80,
            "maxIncome": 500000,
            "category": ["General", "SC", "ST", "OBC", "EWS"],
            "educationLevel": ["12th", "Bachelor", "Master"]
        }
    },
    {
        "id": "stem-excellence",
        "title": "STEM Excellence Scholarship",
        "provider": "Science & Technology Ministry",
        "amount": "₹75,000 - ₹3,00,000/year",
        "deadline": "Every September 30",
        "category": "STEM",
        "criteria": "Science stream + Marks > 85% + Income < 8 LPA",
        "tags": ["STEM", "Science", "Technology", "Merit"],
        "rules": {
            "minMarks": 85,
            "maxIncome": 800000,
            "streams": ["Science", "Engineering"],
            "category": ["General", "SC", "ST", "OBC", "EWS"],
            "subjects": ["Physics", "Chemistry", "Mathematics", "Biology", "Computer"]
        }
    },
    # ============ Income-Based Scholarships ============
    {
        "id": "bpl-scholarship",
        "title": "Below Poverty Line (BPL) Scholarship",
        "provider": "State Government",
        "amount": "₹1,000 - ₹3,000/month + Fees",
        "deadline": "Rolling",
        "category": "Income Support",
        "criteria": "Family Income < 1 LPA",
        "tags": ["BPL", "Income", "Welfare"],
        "rules": {
            "maxIncome": 100000,
            "minMarks": 0,
            "category": ["SC", "ST", "OBC", "General", "EWS"],
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    {
        "id": "low-income-scholarship",
        "title": "Low Income Family Scholarship",
        "provider": "Central Government",
        "amount": "₹2,000 - ₹5,000/month",
        "deadline": "Every July 31",
        "category": "Income Support",
        "criteria": "Family Income 1-3 LPA",
        "tags": ["Income", "Welfare", "Support"],
        "rules": {
            "minIncome": 100000,
            "maxIncome": 300000,
            "minMarks": 0,
            "category": ["SC", "ST", "OBC", "General", "EWS"],
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    # ============ First Generation Scholarships ============
    {
        "id": "first-gen-scholar",
        "title": "First Generation Scholar Program",
        "provider": "Ministry of Education",
        "amount": "₹3,000 - ₹8,000/month + Mentoring",
        "deadline": "Every October 31",
        "category": "First Generation",
        "criteria": "First graduate in family + Marks > 60%",
        "tags": ["First-Generation", "Education", "Mentoring"],
        "rules": {
            "isFirstGraduate": True,
            "minMarks": 60,
            "maxIncome": 500000,
            "category": ["SC", "ST", "OBC", "General", "EWS"],
            "educationLevel": ["12th", "Bachelor", "Master"]
        }
    },
    # ============ Minority Scholarships ============
    {
        "id": "minority-scholarship",
        "title": "Minority Community Scholarship",
        "provider": "Ministry of Minority Affairs",
        "amount": "₹2,000 - ₹6,000/month",
        "deadline": "Every September 30",
        "category": "Minority",
        "criteria": "Minority religion + Income < 2.5 LPA",
        "tags": ["Minority", "Community", "Religious"],
        "rules": {
            "maxIncome": 250000,
            "minMarks": 0,
            "religions": ["Islam", "Christianity", "Sikhism", "Buddhism", "Jainism", "Zoroastrianism"],
            "category": ["General", "OBC"],
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    # ============ Farmer/Rural Scholarships ============
    {
        "id": "farmer-child-scholarship",
        "title": "Farmer's Child Scholarship",
        "provider": "Agricultural Ministry",
        "amount": "₹2,500 - ₹7,000/month",
        "deadline": "Every June 30",
        "category": "Rural Support",
        "criteria": "Parent is farmer + Income < 3 LPA + Marks > 50%",
        "tags": ["Farmer", "Rural", "Agriculture"],
        "rules": {
            "parentOccupations": ["Farmer", "Agriculture"],
            "maxIncome": 300000,
            "minMarks": 50,
            "category": ["SC", "ST", "OBC", "General"],
            "educationLevel": ["10th", "12th", "Bachelor"]
        }
    },
    # ============ Labour Welfare Scholarships ============
    {
        "id": "labour-welfare",
        "title": "Labour Welfare Scholarship",
        "provider": "Labour Ministry",
        "amount": "₹2,000 - ₹6,000/month + Health Benefits",
        "deadline": "Every August 31",
        "category": "Labour Support",
        "criteria": "Parent is laborer/daily wage + Income < 2 LPA",
        "tags": ["Labour", "Welfare", "Daily-Wage"],
        "rules": {
            "parentOccupations": ["Labour", "Daily Wage", "Labourer", "Construction Worker"],
            "maxIncome": 200000,
            "minMarks": 0,
            "category": ["SC", "ST", "OBC", "General"],
            "educationLevel": ["10th", "12th", "Bachelor"]
        }
    },
    # ============ Women Empowerment Scholarships ============
    {
        "id": "women-empowerment",
        "title": "Women Empowerment Scholarship",
        "provider": "Ministry of Women & Child Development",
        "amount": "₹3,000 - ₹8,000/month + Mentoring",
        "deadline": "Rolling",
        "category": "Gender Support",
        "criteria": "Female student + Marks > 50% + Income < 3 LPA",
        "tags": ["Women", "Gender", "Empowerment"],
        "rules": {
            "gender": "Female",
            "minMarks": 50,
            "maxIncome": 300000,
            "category": ["SC", "ST", "OBC", "General", "EWS"],
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    # ============ EWS Scholarships ============
    {
        "id": "ews-post-matric",
        "title": "EWS Post Matric Scholarship",
        "provider": "Ministry of Social Justice",
        "amount": "₹2,500 - ₹5,000/month",
        "deadline": "Every June 30",
        "category": "EWS",
        "criteria": "EWS category + Family Income < 2.5 LPA",
        "tags": ["EWS", "Post-Matric", "Government"],
        "rules": {
            "category": "EWS",
            "maxIncome": 250000,
            "minMarks": 0,
            "educationLevel": ["10th", "12th", "Bachelor", "Master"]
        }
    },
    # ============ State-Specific Scholarships ============
    {
        "id": "delhi-scholar",
        "title": "Delhi Student Scholarship",
        "provider": "Delhi Government",
        "amount": "₹3,000 - ₹10,000/month",
        "deadline": "Every December 31",
        "category": "State Specific",
        "criteria": "Resident of Delhi + Marks > 65%",
        "tags": ["Delhi", "State", "Regional"],
        "rules": {
            "region": "Delhi",
            "minMarks": 65,
            "maxIncome": 600000,
            "category": ["General", "SC", "ST", "OBC", "EWS"],
            "educationLevel": ["10th", "12th", "Bachelor"]
        }
    }
]


def parse_income_to_number(income_level: str) -> float:
    """Convert income level string to numerical value"""
    income_map = {
        "< 1 LPA": 100000,
        "< 2 LPA": 200000,
        "< 3 LPA": 300000,
        "< 5 LPA": 500000,
        "> 5 LPA": 600000,
        "1-3 LPA": 200000,
        "3-5 LPA": 400000
    }
    return income_map.get(income_level, 300000)


def calculate_match_score(student: StudentProfile, scholarship: Dict[str, Any]) -> float:
    """Calculate match score for a student with a scholarship (0-100)"""
    score = 0
    max_possible_score = 100
    
    rules = scholarship.get("rules", {})
    
    # Category matching (30 points)
    if "category" in rules:
        category_rules = rules["category"] if isinstance(rules["category"], list) else [rules["category"]]
        if (student.category or "General") in category_rules:
            score += 30
    else:
        score += 30  # No category restriction
    
    # Income matching (25 points)
    if "maxIncome" in rules:
        student_income = student.family_annual_income or parse_income_to_number(student.income_level)
        if student_income <= rules["maxIncome"]:
            score += 25
        else:
            # Partial points if slightly over
            diff = student_income - rules["maxIncome"]
            if diff < student_income * 0.1:
                score += 15
    else:
        score += 25  # No income restriction
    
    # Marks matching (20 points)
    if "minMarks" in rules:
        if student.overall_percentage >= rules["minMarks"]:
            score += 20
        elif student.overall_percentage >= rules["minMarks"] - 5:
            score += 10  # Close but not quite
    else:
        score += 20  # No marks restriction
    
    # Gender matching (10 points)
    if "gender" in rules:
        if student.gender == rules["gender"]:
            score += 10
    else:
        score += 10
    
    # First generation matching (5 points)
    if "isFirstGraduate" in rules:
        if student.is_first_graduate == rules["isFirstGraduate"]:
            score += 5
    else:
        score += 5
    
    # Parent occupation matching (5 points)
    if "parentOccupations" in rules:
        if student.parent_occupation in rules["parentOccupations"]:
            score += 5
    else:
        score += 5
    
    # Religion matching (5 points)
    if "religions" in rules:
        if student.religion in rules["religions"]:
            score += 5
    else:
        score += 5
    
    return min(score, 100)


def generate_autofill_statement(student: StudentProfile, scholarship: Dict[str, Any], match_score: float) -> str:
    """Generate personalized statement for scholarship application"""
    parts = []
    
    parts.append(f"I am {student.name}, a dedicated student from {student.region}")
    
    if student.category:
        parts.append(f"belonging to {student.category} category")
    
    parts.append(f"with an overall percentage of {student.overall_percentage}%.")
    
    if student.family_annual_income:
        parts.append(f"My family's annual income is ₹{student.family_annual_income:,.0f}.")
    elif student.income_level:
        parts.append(f"My family income is {student.income_level}.")
    
    if student.is_first_graduate:
        parts.append("I am the first graduate in my family, striving to break barriers through education.")
    
    if student.parent_occupation:
        parts.append(f"My parent works as a {student.parent_occupation}.")
    
    parts.append(f"I am applying for {scholarship['title']} to support my educational journey.")
    
    return " ".join(parts)


def find_matching_scholarships(student: StudentProfile, min_score: float = 50) -> List[MatchResult]:
    """Find all scholarships matching a student's profile"""
    matches = []
    
    for scholarship in SCHOLARSHIPS_DATABASE:
        score = calculate_match_score(student, scholarship)
        
        if score >= min_score:
            reason_parts = []
            
            if score >= 90:
                reason_parts.append("Excellent match!")
            elif score >= 75:
                reason_parts.append("Strong match!")
            elif score >= 60:
                reason_parts.append("Good match")
            else:
                reason_parts.append("Eligible")
            
            # Add specific reasons
            rules = scholarship.get("rules", {})
            
            if "category" in rules:
                cat_list = rules["category"] if isinstance(rules["category"], list) else [rules["category"]]
                if (student.category or "General") in cat_list:
                    reason_parts.append(f"matches {student.category} category")
            
            if "minMarks" in rules and student.overall_percentage >= rules["minMarks"]:
                reason_parts.append(f"meets {rules['minMarks']}% marks requirement")
            
            if "maxIncome" in rules:
                student_income = student.family_annual_income or parse_income_to_number(student.income_level)
                if student_income <= rules["maxIncome"]:
                    reason_parts.append(f"income under ₹{rules['maxIncome']:,}")
            
            reason = ". ".join(reason_parts) + "."
            autofill = generate_autofill_statement(student, scholarship, score)
            
            match = MatchResult(
                id=scholarship["id"],
                title=scholarship["title"],
                provider=scholarship["provider"],
                amount=scholarship["amount"],
                deadline=scholarship["deadline"],
                category=scholarship["category"],
                criteria=scholarship["criteria"],
                tags=scholarship["tags"],
                match_score=score,
                reason=reason,
                autofill_statement=autofill
            )
            matches.append(match)
    
    # Sort by match score descending
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return matches


def get_scholarship_by_id(scholarship_id: str) -> Optional[Dict[str, Any]]:
    """Get scholarship details by ID"""
    for scholarship in SCHOLARSHIPS_DATABASE:
        if scholarship["id"] == scholarship_id:
            return scholarship
    return None
