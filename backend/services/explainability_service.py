"""
Explainable Decision Service for Student Scholarship Application
Provides transparent, detailed explanations for eligibility decisions
Shows exactly why a student is eligible or not eligible for each scholarship
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class EligibilityExplainer:
    """
    Generates human-readable explanations for scholarship eligibility decisions
    """
    
    def __init__(self):
        self.checks_performed = []
        self.passed_checks = []
        self.failed_checks = []
        self.warnings = []
    
    def reset(self):
        """Reset all tracking lists"""
        self.checks_performed = []
        self.passed_checks = []
        self.failed_checks = []
        self.warnings = []
    
    def add_check(self, criterion: str, passed: bool, reason: str, details: Dict = None):
        """Add an eligibility check result"""
        check = {
            "criterion": criterion,
            "passed": passed,
            "reason": reason,
            "details": details or {}
        }
        self.checks_performed.append(check)
        
        if passed:
            self.passed_checks.append(check)
        else:
            self.failed_checks.append(check)
    
    def add_warning(self, message: str):
        """Add a warning (non-blocking issue)"""
        self.warnings.append(message)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get eligibility check summary"""
        is_eligible = len(self.failed_checks) == 0
        
        return {
            "isEligible": is_eligible,
            "totalChecks": len(self.checks_performed),
            "passedChecks": len(self.passed_checks),
            "failedChecks": len(self.failed_checks),
            "warnings": len(self.warnings)
        }
    
    def get_full_report(self) -> Dict[str, Any]:
        """Get complete eligibility report with explanations"""
        summary = self.get_summary()
        
        return {
            **summary,
            "checks": self.checks_performed,
            "passed": self.passed_checks,
            "failed": self.failed_checks,
            "warningMessages": self.warnings,
            "generatedAt": datetime.utcnow().isoformat()
        }


def explain_eligibility(
    student: Dict[str, Any],
    scholarship: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed explanation of why a student is or isn't eligible for a scholarship
    
    Args:
        student: Student profile data
        scholarship: Scholarship details with eligibility rules
        
    Returns:
        Comprehensive eligibility explanation
    """
    explainer = EligibilityExplainer()
    rules = scholarship.get("rules", {})
    
    # ==================== CATEGORY CHECK ====================
    if "category" in rules:
        required_category = rules["category"]
        student_category = student.get("category")
        
        if isinstance(required_category, list):
            # Multiple categories allowed
            passed = student_category in required_category
            if passed:
                explainer.add_check(
                    criterion="Category",
                    passed=True,
                    reason=f"[PASS] Student category '{student_category}' is accepted (allowed: {', '.join(required_category)})",
                    details={
                        "required": required_category,
                        "student_value": student_category
                    }
                )
            else:
                explainer.add_check(
                    criterion="Category",
                    passed=False,
                    reason=f"[FAIL] Student category '{student_category}' not in allowed categories: {', '.join(required_category)}",
                    details={
                        "required": required_category,
                        "student_value": student_category
                    }
                )
        else:
            # Single category required
            passed = student_category == required_category
            if passed:
                explainer.add_check(
                    criterion="Category",
                    passed=True,
                    reason=f"[PASS] Student belongs to required category: {required_category}",
                    details={
                        "required": required_category,
                        "student_value": student_category
                    }
                )
            else:
                explainer.add_check(
                    criterion="Category",
                    passed=False,
                    reason=f"[FAIL] Category mismatch - Required: {required_category}, Student: {student_category}",
                    details={
                        "required": required_category,
                        "student_value": student_category
                    }
                )
    
    # ==================== INCOME CHECK ====================
    if "maxIncome" in rules:
        max_income = rules["maxIncome"]
        student_income = _parse_income(student.get("incomeLevel", "0"))
        
        passed = student_income <= max_income
        income_lpa = max_income / 100000
        student_income_lpa = student_income / 100000
        
        if passed:
            explainer.add_check(
                criterion="Income Limit",
                passed=True,
                reason=f"[PASS] Family income Rs.{student_income_lpa:.1f} LPA is within limit of Rs.{income_lpa:.1f} LPA",
                details={
                    "max_allowed": max_income,
                    "student_income": student_income,
                    "max_allowed_lpa": income_lpa,
                    "student_income_lpa": student_income_lpa
                }
            )
        else:
            explainer.add_check(
                criterion="Income Limit",
                passed=False,
                reason=f"[FAIL] Family income Rs.{student_income_lpa:.1f} LPA exceeds limit of Rs.{income_lpa:.1f} LPA",
                details={
                    "max_allowed": max_income,
                    "student_income": student_income,
                    "exceeded_by": student_income - max_income
                }
            )
    
    # ==================== MARKS/PERCENTAGE CHECK ====================
    if "minMarks" in rules:
        min_marks = rules["minMarks"]
        student_marks = student.get("overallPercentage", 0)
        
        passed = student_marks >= min_marks
        
        if passed:
            explainer.add_check(
                criterion="Minimum Marks",
                passed=True,
                reason=f"[PASS] Academic score {student_marks}% meets minimum requirement of {min_marks}%",
                details={
                    "required": min_marks,
                    "student_score": student_marks,
                    "margin": student_marks - min_marks
                }
            )
        else:
            explainer.add_check(
                criterion="Minimum Marks",
                passed=False,
                reason=f"[FAIL] Academic score {student_marks}% is below minimum requirement of {min_marks}%",
                details={
                    "required": min_marks,
                    "student_score": student_marks,
                    "shortfall": min_marks - student_marks
                }
            )
    
    # ==================== EDUCATION LEVEL CHECK ====================
    if "educationLevel" in rules:
        required_levels = rules["educationLevel"]
        student_level = student.get("educationLevel", "Unknown")
        
        if isinstance(required_levels, list):
            passed = student_level in required_levels or any(
                level.lower() in student_level.lower() 
                for level in required_levels
            )
        else:
            passed = student_level.lower() == required_levels.lower()
        
        if passed:
            explainer.add_check(
                criterion="Education Level",
                passed=True,
                reason=f"[PASS] Education level '{student_level}' is eligible",
                details={
                    "required_levels": required_levels,
                    "student_level": student_level
                }
            )
        else:
            explainer.add_check(
                criterion="Education Level",
                passed=False,
                reason=f"[FAIL] Education level '{student_level}' not in required: {required_levels}",
                details={
                    "required_levels": required_levels,
                    "student_level": student_level
                }
            )
    
    # ==================== GENDER CHECK ====================
    if "gender" in rules:
        required_gender = rules["gender"]
        student_gender = student.get("gender")
        
        if isinstance(required_gender, list):
            passed = student_gender in required_gender
        else:
            passed = student_gender == required_gender
        
        if passed:
            explainer.add_check(
                criterion="Gender",
                passed=True,
                reason=f"[PASS] Gender requirement met: {student_gender}",
                details={
                    "required": required_gender,
                    "student_gender": student_gender
                }
            )
        else:
            explainer.add_check(
                criterion="Gender",
                passed=False,
                reason=f"[FAIL] Gender '{student_gender}' does not match required: {required_gender}",
                details={
                    "required": required_gender,
                    "student_gender": student_gender
                }
            )
    
    # ==================== REGION/STATE CHECK ====================
    if "region" in rules or "state" in rules:
        required_regions = rules.get("region") or rules.get("state")
        student_region = student.get("region", "Unknown")
        
        if isinstance(required_regions, list):
            passed = any(
                r.lower() in student_region.lower() or student_region.lower() in r.lower()
                for r in required_regions
            )
        else:
            passed = required_regions.lower() in student_region.lower()
        
        if passed:
            explainer.add_check(
                criterion="Region/State",
                passed=True,
                reason=f"[PASS] Region '{student_region}' is eligible",
                details={
                    "required_regions": required_regions,
                    "student_region": student_region
                }
            )
        else:
            explainer.add_check(
                criterion="Region/State",
                passed=False,
                reason=f"[FAIL] Region '{student_region}' not in eligible regions: {required_regions}",
                details={
                    "required_regions": required_regions,
                    "student_region": student_region
                }
            )
    
    # ==================== FIRST GRADUATE CHECK ====================
    if "firstGraduate" in rules and rules["firstGraduate"]:
        is_first_grad = student.get("isFirstGraduate", False)
        
        if is_first_grad:
            explainer.add_check(
                criterion="First Graduate",
                passed=True,
                reason="[PASS] Student is first graduate in family",
                details={"is_first_graduate": True}
            )
        else:
            explainer.add_check(
                criterion="First Graduate",
                passed=False,
                reason="[FAIL] This scholarship requires the student to be first graduate in family",
                details={"is_first_graduate": False}
            )
    
    # ==================== AGE CHECK ====================
    if "minAge" in rules or "maxAge" in rules:
        student_age = student.get("age")
        
        if student_age:
            min_age = rules.get("minAge", 0)
            max_age = rules.get("maxAge", 100)
            
            passed = min_age <= student_age <= max_age
            
            if passed:
                explainer.add_check(
                    criterion="Age Requirement",
                    passed=True,
                    reason=f"[PASS] Age {student_age} is within allowed range ({min_age}-{max_age} years)",
                    details={
                        "min_age": min_age,
                        "max_age": max_age,
                        "student_age": student_age
                    }
                )
            else:
                explainer.add_check(
                    criterion="Age Requirement",
                    passed=False,
                    reason=f"[FAIL] Age {student_age} is outside allowed range ({min_age}-{max_age} years)",
                    details={
                        "min_age": min_age,
                        "max_age": max_age,
                        "student_age": student_age
                    }
                )
        else:
            explainer.add_warning("Age not provided - age requirement not verified")
    
    # ==================== SUBJECT/STREAM CHECK ====================
    if "subjects" in rules or "streams" in rules:
        required = rules.get("subjects") or rules.get("streams")
        student_marks = student.get("marks", [])
        student_subjects = [m.get("subject", "").lower() for m in student_marks if isinstance(m, dict)]
        
        if student_subjects:
            matched = any(
                any(req.lower() in subj or subj in req.lower() for subj in student_subjects)
                for req in required
            )
            
            if matched:
                explainer.add_check(
                    criterion="Subject/Stream",
                    passed=True,
                    reason=f"✅ Student has relevant subjects for this scholarship",
                    details={
                        "required_subjects": required,
                        "student_subjects": student_subjects
                    }
                )
            else:
                explainer.add_check(
                    criterion="Subject/Stream",
                    passed=False,
                    reason=f"❌ Required subjects not found: {required}",
                    details={
                        "required_subjects": required,
                        "student_subjects": student_subjects
                    }
                )
        else:
            explainer.add_warning("Subject details not provided - stream requirement not fully verified")
    
    # ==================== GENERATE FINAL REPORT ====================
    report = explainer.get_full_report()
    
    # Add overall eligibility statement
    if report["isEligible"]:
        report["statement"] = f"✅ ELIGIBLE: Student meets all {report['totalChecks']} criteria for {scholarship.get('title', 'this scholarship')}"
        report["recommendation"] = "Recommended to apply"
    else:
        failed_criteria = [c["criterion"] for c in report["failed"]]
        report["statement"] = f"❌ NOT ELIGIBLE: Failed {report['failedChecks']} of {report['totalChecks']} criteria ({', '.join(failed_criteria)})"
        report["recommendation"] = "Does not meet eligibility requirements"
    
    # Add scholarship info
    report["scholarship"] = {
        "id": scholarship.get("id"),
        "title": scholarship.get("title"),
        "provider": scholarship.get("provider"),
        "amount": scholarship.get("amount"),
        "deadline": scholarship.get("deadline")
    }
    
    return report


def explain_all_scholarships(
    student: Dict[str, Any],
    scholarships: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate eligibility explanations for all scholarships
    
    Args:
        student: Student profile
        scholarships: List of scholarships to check
        
    Returns:
        Complete eligibility report for all scholarships
    """
    results = {
        "student": {
            "name": student.get("name"),
            "category": student.get("category"),
            "percentage": student.get("overallPercentage"),
            "incomeLevel": student.get("incomeLevel"),
            "region": student.get("region")
        },
        "totalScholarships": len(scholarships),
        "eligible": [],
        "notEligible": [],
        "eligibleCount": 0,
        "notEligibleCount": 0,
        "detailedReports": [],
        "generatedAt": datetime.utcnow().isoformat()
    }
    
    for scholarship in scholarships:
        report = explain_eligibility(student, scholarship)
        results["detailedReports"].append(report)
        
        if report["isEligible"]:
            results["eligible"].append({
                "id": scholarship.get("id"),
                "title": scholarship.get("title"),
                "amount": scholarship.get("amount"),
                "matchedCriteria": report["passedChecks"]
            })
            results["eligibleCount"] += 1
        else:
            results["notEligible"].append({
                "id": scholarship.get("id"),
                "title": scholarship.get("title"),
                "failedCriteria": [c["criterion"] for c in report["failed"]],
                "reasons": [c["reason"] for c in report["failed"]]
            })
            results["notEligibleCount"] += 1
    
    # Summary
    results["summary"] = {
        "message": f"Student is eligible for {results['eligibleCount']} out of {results['totalScholarships']} scholarships",
        "eligibilityRate": round((results['eligibleCount'] / results['totalScholarships']) * 100, 1) if results['totalScholarships'] > 0 else 0
    }
    
    return results


def _parse_income(income_str: str) -> float:
    """Parse income string to numeric value"""
    import re
    
    if isinstance(income_str, (int, float)):
        return float(income_str)
    
    income_str = str(income_str).upper().strip()
    
    # Extract numbers
    numbers = re.findall(r'[\d.]+', income_str.replace(',', ''))
    
    if numbers:
        value = float(numbers[0])
        
        # Convert LPA to annual
        if 'LPA' in income_str or 'LAKH' in income_str:
            value *= 100000
        elif value < 100:  # Assume lakhs
            value *= 100000
        
        return value
    
    # Default mappings
    income_mappings = {
        "< 2 LPA": 150000,
        "< 2.5 LPA": 200000,
        "< 5 LPA": 400000,
        "< 8 LPA": 700000,
        "> 8 LPA": 1000000,
        "BPL": 50000
    }
    
    for key, val in income_mappings.items():
        if key in income_str:
            return val
    
    return 0


def generate_eligibility_summary(
    is_eligible: bool,
    checks_passed: int,
    checks_failed: int,
    failed_criteria: List[str]
) -> str:
    """
    Generate a human-readable eligibility summary
    """
    if is_eligible:
        return f"✅ Eligible - All {checks_passed} criteria met"
    else:
        return f"❌ Not Eligible - Failed: {', '.join(failed_criteria)}"
