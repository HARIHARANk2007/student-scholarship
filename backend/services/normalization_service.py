"""
Data Normalization Service for Student Scholarship Application
Converts different marking schemes (CGPA, Grades, Percentage) into a common format
Ensures fair and consistent evaluation across all students
"""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class GradeSystem(str, Enum):
    """Different grading systems used in education"""
    PERCENTAGE = "percentage"
    CGPA_10 = "cgpa_10"  # CGPA out of 10
    CGPA_4 = "cgpa_4"    # CGPA out of 4 (US system)
    LETTER_GRADE = "letter_grade"
    GPA_5 = "gpa_5"      # GPA out of 5


# ==================== CGPA TO PERCENTAGE CONVERSION ====================

# Standard CGPA (10-point scale) to Percentage mappings
CGPA_10_TO_PERCENTAGE = {
    10.0: 95.0,
    9.5: 92.5,
    9.0: 90.0,
    8.5: 85.0,
    8.0: 80.0,
    7.5: 75.0,
    7.0: 70.0,
    6.5: 65.0,
    6.0: 60.0,
    5.5: 55.0,
    5.0: 50.0,
    4.5: 45.0,
    4.0: 40.0,
    3.5: 35.0,
    3.0: 30.0,
}

# CBSE Standard: Percentage = CGPA × 9.5
def cgpa_to_percentage_cbse(cgpa: float) -> float:
    """
    Convert CGPA to percentage using CBSE formula
    Formula: Percentage = CGPA × 9.5
    
    Args:
        cgpa: CGPA value (0-10 scale)
        
    Returns:
        Equivalent percentage (0-100)
    """
    if cgpa < 0 or cgpa > 10:
        raise ValueError(f"CGPA must be between 0 and 10, got {cgpa}")
    return round(cgpa * 9.5, 2)


def percentage_to_cgpa_cbse(percentage: float) -> float:
    """
    Convert percentage to CGPA using CBSE formula
    Formula: CGPA = Percentage / 9.5
    
    Args:
        percentage: Percentage value (0-100)
        
    Returns:
        Equivalent CGPA (0-10)
    """
    if percentage < 0 or percentage > 100:
        raise ValueError(f"Percentage must be between 0 and 100, got {percentage}")
    return round(percentage / 9.5, 2)


# VTU (Visvesvaraya Technological University) formula
def cgpa_to_percentage_vtu(cgpa: float) -> float:
    """
    Convert CGPA to percentage using VTU formula
    Formula: Percentage = (CGPA - 0.5) × 10
    
    Args:
        cgpa: CGPA value (0-10 scale)
        
    Returns:
        Equivalent percentage (0-100)
    """
    if cgpa < 0 or cgpa > 10:
        raise ValueError(f"CGPA must be between 0 and 10, got {cgpa}")
    return round((cgpa - 0.5) * 10, 2)


# University of Mumbai formula
def cgpa_to_percentage_mumbai(cgpa: float) -> float:
    """
    Convert CGPA to percentage using Mumbai University formula
    Formula: Percentage = 7.1 × CGPA + 11
    
    Args:
        cgpa: CGPA value (0-10 scale)
        
    Returns:
        Equivalent percentage (0-100)
    """
    if cgpa < 0 or cgpa > 10:
        raise ValueError(f"CGPA must be between 0 and 10, got {cgpa}")
    return round(7.1 * cgpa + 11, 2)


# Generic conversion (most common)
def cgpa_to_percentage_generic(cgpa: float, scale: float = 10.0) -> float:
    """
    Generic CGPA to percentage conversion
    Formula: Percentage = (CGPA / Scale) × 100
    
    Args:
        cgpa: CGPA value
        scale: Maximum CGPA (default 10)
        
    Returns:
        Equivalent percentage (0-100)
    """
    if cgpa < 0 or cgpa > scale:
        raise ValueError(f"CGPA must be between 0 and {scale}, got {cgpa}")
    return round((cgpa / scale) * 100, 2)


# ==================== LETTER GRADE CONVERSION ====================

# Standard letter grade to percentage mapping (Indian system)
LETTER_GRADE_TO_PERCENTAGE_INDIA = {
    "O": 95,    # Outstanding
    "A+": 90,   # Excellent
    "A": 85,    # Very Good
    "B+": 75,   # Good
    "B": 65,    # Above Average
    "C+": 55,   # Average
    "C": 50,    # Satisfactory
    "D": 45,    # Pass
    "E": 40,    # Marginal Pass
    "F": 0,     # Fail
    "AB": 0,    # Absent
}

# US letter grade system
LETTER_GRADE_TO_PERCENTAGE_US = {
    "A+": 97,
    "A": 93,
    "A-": 90,
    "B+": 87,
    "B": 83,
    "B-": 80,
    "C+": 77,
    "C": 73,
    "C-": 70,
    "D+": 67,
    "D": 63,
    "D-": 60,
    "F": 0,
}

# Letter grade to CGPA (10-point scale)
LETTER_GRADE_TO_CGPA = {
    "O": 10.0,
    "A+": 9.5,
    "A": 9.0,
    "B+": 8.0,
    "B": 7.0,
    "C+": 6.0,
    "C": 5.0,
    "D": 4.0,
    "E": 3.5,
    "F": 0.0,
}


def letter_grade_to_percentage(grade: str, system: str = "india") -> float:
    """
    Convert letter grade to percentage
    
    Args:
        grade: Letter grade (A+, A, B+, etc.)
        system: Grading system ('india' or 'us')
        
    Returns:
        Equivalent percentage
    """
    grade_upper = grade.upper().strip()
    
    if system.lower() == "india":
        mapping = LETTER_GRADE_TO_PERCENTAGE_INDIA
    else:
        mapping = LETTER_GRADE_TO_PERCENTAGE_US
    
    if grade_upper in mapping:
        return float(mapping[grade_upper])
    
    # Try to find closest match
    for key in mapping:
        if key in grade_upper or grade_upper in key:
            return float(mapping[key])
    
    raise ValueError(f"Unknown grade: {grade}")


def letter_grade_to_cgpa(grade: str) -> float:
    """
    Convert letter grade to CGPA (10-point scale)
    
    Args:
        grade: Letter grade (A+, A, B+, etc.)
        
    Returns:
        Equivalent CGPA
    """
    grade_upper = grade.upper().strip()
    
    if grade_upper in LETTER_GRADE_TO_CGPA:
        return LETTER_GRADE_TO_CGPA[grade_upper]
    
    raise ValueError(f"Unknown grade: {grade}")


# ==================== GPA 4.0 SCALE CONVERSION ====================

def gpa4_to_percentage(gpa: float) -> float:
    """
    Convert GPA (4.0 scale) to percentage
    
    Standard mapping:
    4.0 = 90-100% (A)
    3.0 = 80-89% (B)
    2.0 = 70-79% (C)
    1.0 = 60-69% (D)
    0.0 = Below 60% (F)
    
    Args:
        gpa: GPA value (0-4 scale)
        
    Returns:
        Equivalent percentage
    """
    if gpa < 0 or gpa > 4:
        raise ValueError(f"GPA must be between 0 and 4, got {gpa}")
    
    # Linear interpolation
    if gpa >= 4.0:
        return 95.0
    elif gpa >= 3.7:
        return 90.0 + (gpa - 3.7) * (95 - 90) / 0.3
    elif gpa >= 3.3:
        return 87.0 + (gpa - 3.3) * (90 - 87) / 0.4
    elif gpa >= 3.0:
        return 83.0 + (gpa - 3.0) * (87 - 83) / 0.3
    elif gpa >= 2.7:
        return 80.0 + (gpa - 2.7) * (83 - 80) / 0.3
    elif gpa >= 2.3:
        return 77.0 + (gpa - 2.3) * (80 - 77) / 0.4
    elif gpa >= 2.0:
        return 73.0 + (gpa - 2.0) * (77 - 73) / 0.3
    elif gpa >= 1.7:
        return 70.0 + (gpa - 1.7) * (73 - 70) / 0.3
    elif gpa >= 1.3:
        return 67.0 + (gpa - 1.3) * (70 - 67) / 0.4
    elif gpa >= 1.0:
        return 63.0 + (gpa - 1.0) * (67 - 63) / 0.3
    elif gpa >= 0.7:
        return 60.0 + (gpa - 0.7) * (63 - 60) / 0.3
    else:
        return gpa * 60 / 0.7


def percentage_to_gpa4(percentage: float) -> float:
    """
    Convert percentage to GPA (4.0 scale)
    
    Args:
        percentage: Percentage value (0-100)
        
    Returns:
        Equivalent GPA (0-4)
    """
    if percentage < 0 or percentage > 100:
        raise ValueError(f"Percentage must be between 0 and 100, got {percentage}")
    
    if percentage >= 93:
        return 4.0
    elif percentage >= 90:
        return 3.7
    elif percentage >= 87:
        return 3.3
    elif percentage >= 83:
        return 3.0
    elif percentage >= 80:
        return 2.7
    elif percentage >= 77:
        return 2.3
    elif percentage >= 73:
        return 2.0
    elif percentage >= 70:
        return 1.7
    elif percentage >= 67:
        return 1.3
    elif percentage >= 63:
        return 1.0
    elif percentage >= 60:
        return 0.7
    else:
        return 0.0


# ==================== SMART AUTO-DETECTION ====================

def detect_score_type(score: Any) -> Tuple[GradeSystem, Any]:
    """
    Automatically detect the type of score and return normalized value
    
    Args:
        score: Raw score value (can be string, float, or int)
        
    Returns:
        Tuple of (GradeSystem, normalized_value)
    """
    # Handle string scores
    if isinstance(score, str):
        score = score.strip().upper()
        
        # Check if it's a letter grade
        if score in LETTER_GRADE_TO_PERCENTAGE_INDIA or score in LETTER_GRADE_TO_PERCENTAGE_US:
            return (GradeSystem.LETTER_GRADE, score)
        
        # Check if it contains % symbol
        if '%' in score:
            try:
                return (GradeSystem.PERCENTAGE, float(score.replace('%', '').strip()))
            except ValueError:
                pass
        
        # Try to parse as number
        try:
            score = float(score)
        except ValueError:
            # Might be a grade like "A+" or "B"
            return (GradeSystem.LETTER_GRADE, score)
    
    # Handle numeric scores
    if isinstance(score, (int, float)):
        if score > 10:
            # Likely percentage
            return (GradeSystem.PERCENTAGE, float(score))
        elif score > 4:
            # Likely CGPA (10-point scale)
            return (GradeSystem.CGPA_10, float(score))
        elif score <= 4:
            # Likely GPA (4.0 scale)
            return (GradeSystem.CGPA_4, float(score))
    
    return (GradeSystem.PERCENTAGE, 0.0)


# ==================== UNIFIED NORMALIZATION FUNCTION ====================

def normalize_to_percentage(
    score: Any,
    score_type: Optional[str] = None,
    university: Optional[str] = None
) -> Dict[str, Any]:
    """
    Universal function to normalize any score to percentage
    
    Args:
        score: Raw score (CGPA, GPA, Letter Grade, or Percentage)
        score_type: Optional hint about score type ('cgpa', 'gpa', 'grade', 'percentage')
        university: Optional university name for specific conversion formula
        
    Returns:
        Dictionary with:
        - percentage: Normalized percentage value
        - original_score: Original input score
        - detected_type: Type of score detected
        - conversion_method: Method used for conversion
        - cgpa_10: Equivalent CGPA on 10-point scale
        - gpa_4: Equivalent GPA on 4.0 scale
        - letter_grade: Equivalent letter grade
    """
    result = {
        "original_score": score,
        "detected_type": None,
        "conversion_method": None,
        "percentage": 0.0,
        "cgpa_10": 0.0,
        "gpa_4": 0.0,
        "letter_grade": "F"
    }
    
    try:
        # Auto-detect score type if not provided
        if score_type:
            score_type_lower = score_type.lower()
            if 'cgpa' in score_type_lower or score_type_lower == 'cgpa_10':
                detected_type = GradeSystem.CGPA_10
                score_value = float(score) if not isinstance(score, str) else float(score)
            elif 'gpa' in score_type_lower or score_type_lower == 'cgpa_4':
                detected_type = GradeSystem.CGPA_4
                score_value = float(score)
            elif 'grade' in score_type_lower:
                detected_type = GradeSystem.LETTER_GRADE
                score_value = str(score).upper()
            else:
                detected_type = GradeSystem.PERCENTAGE
                score_value = float(score)
        else:
            detected_type, score_value = detect_score_type(score)
        
        result["detected_type"] = detected_type.value
        
        # Convert to percentage based on type
        if detected_type == GradeSystem.PERCENTAGE:
            percentage = float(score_value)
            result["conversion_method"] = "direct"
            
        elif detected_type == GradeSystem.CGPA_10:
            # Choose conversion formula based on university
            if university:
                uni_lower = university.lower()
                if 'vtu' in uni_lower or 'visvesvaraya' in uni_lower:
                    percentage = cgpa_to_percentage_vtu(score_value)
                    result["conversion_method"] = "VTU formula: (CGPA - 0.5) × 10"
                elif 'mumbai' in uni_lower:
                    percentage = cgpa_to_percentage_mumbai(score_value)
                    result["conversion_method"] = "Mumbai University formula: 7.1 × CGPA + 11"
                else:
                    percentage = cgpa_to_percentage_cbse(score_value)
                    result["conversion_method"] = "CBSE formula: CGPA × 9.5"
            else:
                percentage = cgpa_to_percentage_cbse(score_value)
                result["conversion_method"] = "CBSE formula: CGPA × 9.5"
                
        elif detected_type == GradeSystem.CGPA_4:
            percentage = gpa4_to_percentage(score_value)
            result["conversion_method"] = "GPA 4.0 scale conversion"
            
        elif detected_type == GradeSystem.LETTER_GRADE:
            percentage = letter_grade_to_percentage(score_value)
            result["conversion_method"] = "Letter grade mapping"
        
        else:
            percentage = 0.0
            result["conversion_method"] = "unknown"
        
        # Store percentage and calculate equivalents
        result["percentage"] = round(percentage, 2)
        result["cgpa_10"] = round(percentage_to_cgpa_cbse(percentage), 2) if percentage > 0 else 0.0
        result["gpa_4"] = round(percentage_to_gpa4(percentage), 2) if percentage > 0 else 0.0
        result["letter_grade"] = percentage_to_letter_grade(percentage)
        
    except Exception as e:
        result["error"] = str(e)
        result["conversion_method"] = "failed"
    
    return result


def percentage_to_letter_grade(percentage: float) -> str:
    """
    Convert percentage to letter grade (Indian system)
    
    Args:
        percentage: Percentage value (0-100)
        
    Returns:
        Letter grade
    """
    if percentage >= 90:
        return "O"
    elif percentage >= 80:
        return "A+"
    elif percentage >= 70:
        return "A"
    elif percentage >= 60:
        return "B+"
    elif percentage >= 50:
        return "B"
    elif percentage >= 45:
        return "C+"
    elif percentage >= 40:
        return "C"
    elif percentage >= 35:
        return "D"
    else:
        return "F"


# ==================== INCOME NORMALIZATION ====================

def normalize_income(income_str: str) -> Dict[str, Any]:
    """
    Normalize income string to numeric value
    
    Handles formats like:
    - "< 2 LPA", "< 2.5 LPA", "> 8 LPA"
    - "2,00,000", "200000"
    - "2 Lakhs", "2L"
    
    Args:
        income_str: Income string
        
    Returns:
        Dictionary with normalized income info
    """
    import re
    
    result = {
        "original": income_str,
        "annual_income": 0,
        "income_category": "unknown",
        "is_below_poverty": False,
        "is_ews": False
    }
    
    income_str = income_str.strip().upper()
    
    # Extract numeric value
    # Match patterns like "2.5", "2,00,000", "200000"
    numbers = re.findall(r'[\d,]+\.?\d*', income_str)
    
    if numbers:
        # Get the first number
        num_str = numbers[0].replace(',', '')
        try:
            value = float(num_str)
            
            # Check for LPA (Lakhs Per Annum)
            if 'LPA' in income_str or 'LAKH' in income_str or 'L' in income_str:
                value = value * 100000
            elif 'K' in income_str:
                value = value * 1000
            elif value < 100:  # Assume it's in lakhs if small number
                value = value * 100000
            
            result["annual_income"] = int(value)
            
        except ValueError:
            pass
    
    # Categorize income
    income = result["annual_income"]
    
    if income <= 100000:
        result["income_category"] = "BPL"
        result["is_below_poverty"] = True
    elif income <= 200000:
        result["income_category"] = "< 2 LPA"
        result["is_ews"] = True
    elif income <= 250000:
        result["income_category"] = "< 2.5 LPA"
        result["is_ews"] = True
    elif income <= 500000:
        result["income_category"] = "< 5 LPA"
    elif income <= 800000:
        result["income_category"] = "< 8 LPA"
    else:
        result["income_category"] = "> 8 LPA"
    
    return result


# ==================== STUDENT PROFILE NORMALIZATION ====================

def normalize_student_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize all academic and financial data in a student profile
    
    Args:
        profile: Student profile dictionary
        
    Returns:
        Normalized profile with standardized values
    """
    normalized = profile.copy()
    
    # Normalize overall percentage/CGPA
    if "overallPercentage" in profile:
        score = profile["overallPercentage"]
        score_type = profile.get("scoreType")
        university = profile.get("university")
        
        normalized_score = normalize_to_percentage(score, score_type, university)
        normalized["overallPercentage"] = normalized_score["percentage"]
        normalized["normalizedScore"] = normalized_score
    
    # Normalize individual subject marks
    if "marks" in profile and isinstance(profile["marks"], list):
        normalized_marks = []
        for mark in profile["marks"]:
            if isinstance(mark, dict):
                subject = mark.get("subject", "Unknown")
                score = mark.get("score", 0)
                max_score = mark.get("maxScore", 100)
                
                # Calculate percentage for this subject
                if max_score > 0:
                    subject_percentage = (score / max_score) * 100
                else:
                    subject_percentage = 0
                
                normalized_marks.append({
                    "subject": subject,
                    "score": score,
                    "maxScore": max_score,
                    "percentage": round(subject_percentage, 2)
                })
        
        normalized["marks"] = normalized_marks
    
    # Normalize income
    if "incomeLevel" in profile:
        income_info = normalize_income(profile["incomeLevel"])
        normalized["normalizedIncome"] = income_info
        normalized["annualIncome"] = income_info["annual_income"]
    
    return normalized


# ==================== QUICK CONVERSION HELPERS ====================

def quick_cgpa_to_percentage(cgpa: float) -> float:
    """Quick conversion using CBSE formula"""
    return cgpa_to_percentage_cbse(cgpa)


def quick_percentage_to_cgpa(percentage: float) -> float:
    """Quick conversion using CBSE formula"""
    return percentage_to_cgpa_cbse(percentage)


def quick_grade_to_percentage(grade: str) -> float:
    """Quick letter grade to percentage conversion"""
    return letter_grade_to_percentage(grade)


# ==================== CONVERSION TABLE GENERATOR ====================

def generate_conversion_table() -> List[Dict]:
    """
    Generate a comprehensive conversion table for reference
    
    Returns:
        List of conversion entries
    """
    table = []
    
    for cgpa in [10.0, 9.5, 9.0, 8.5, 8.0, 7.5, 7.0, 6.5, 6.0, 5.5, 5.0, 4.5, 4.0]:
        percentage = cgpa_to_percentage_cbse(cgpa)
        gpa_4 = percentage_to_gpa4(percentage)
        grade = percentage_to_letter_grade(percentage)
        
        table.append({
            "cgpa_10": cgpa,
            "percentage": percentage,
            "gpa_4": round(gpa_4, 1),
            "letter_grade": grade,
            "description": get_grade_description(grade)
        })
    
    return table


def get_grade_description(grade: str) -> str:
    """Get description for a letter grade"""
    descriptions = {
        "O": "Outstanding",
        "A+": "Excellent",
        "A": "Very Good",
        "B+": "Good",
        "B": "Above Average",
        "C+": "Average",
        "C": "Satisfactory",
        "D": "Pass",
        "F": "Fail"
    }
    return descriptions.get(grade, "Unknown")
