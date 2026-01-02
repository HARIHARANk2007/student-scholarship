"""
AI Mark Extraction Service
Uses Google Gemini API to parse OCR text and extract structured student data
"""

import os
import json
import httpx
import asyncio
from typing import Dict, Any
from pathlib import Path
from models.types import StudentProfile, SubjectMark
from dotenv import load_dotenv

# Load environment variables from .env file
# Look in backend folder first, then parent
load_dotenv(Path(__file__).parent.parent / ".env")
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Gemini API Key - load from environment
# Get your FREE key at: https://aistudio.google.com/apikey
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("[WARN] GEMINI_API_KEY not found in .env file")
    print("   Get your FREE key at: https://aistudio.google.com/apikey")
    print("   Then add to backend/.env: GEMINI_API_KEY=your_key_here")
else:
    print(f"[OK] Gemini API Key loaded (ends with: ...{GEMINI_API_KEY[-8:]})")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


async def parse_marksheet_with_ai(ocr_text: str) -> StudentProfile:
    """
    Parse OCR extracted text using AI to get structured student data
    
    Args:
        ocr_text: Raw text extracted by OCR from marksheet image
        
    Returns:
        Structured student profile with extracted marks
        
    Raises:
        ValueError: If API key is not configured
        Exception: If API request fails
    """
    print("[INFO] Starting AI-powered mark extraction...")
    
    # Check if API key is available
    if not GEMINI_API_KEY:
        print("[WARN] Gemini API key not found")
        raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in .env")
    
    print(f"[INFO] API Key found (length: {len(GEMINI_API_KEY)})")
    
    prompt = f"""You are an expert marksheet analyzer. Parse the following OCR text from a student's marksheet and extract ALL information in JSON format.

OCR Text:
{ocr_text}

CRITICAL: Extract EXACTLY this JSON structure:
{{
  "name": "student full name",
  "percentage": numerical percentage value (e.g., 82),
  "totalMarks": numerical total marks achieved,
  "maxMarks": numerical maximum possible marks,
  "subjects": [
    {{ "subject": "Subject Name", "score": number, "maxScore": number }},
    {{ "subject": "Subject Name", "score": number, "maxScore": number }}
  ],
  "category": "SC/ST/OBC/General/Not Mentioned",
  "incomeLevel": "< 1 LPA / < 2 LPA / < 5 LPA / > 5 LPA / Not Mentioned",
  "parentOccupation": "Farmer/Business/Service/Labor/Not Mentioned",
  "board": "Board/University Name",
  "year": "Year of Exam",
  "confidence": confidence score 0-100
}}

IMPORTANT Rules:
1. If percentage is not explicitly mentioned, calculate from (totalMarks / maxMarks) * 100
2. Extract ALL subject marks found
3. For category, look for SC/ST/OBC/General mentions
4. For income, look for annual income values and convert to LPA format
5. Infer from context if exact values missing
6. Set confidence 90+ if clear data, 70-90 if some inference, <70 if uncertain
7. If field is not found, return "Not Mentioned"

Return ONLY valid JSON, no other text."""

    print("[INFO] Sending request to Gemini API...")
    print(f"[INFO] API URL: {GEMINI_API_URL}")
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
        
        print(f"[INFO] API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", f"API error: {response.status_code}")
            print(f"[ERROR] Gemini API error: {error_msg}")
            print(f"[ERROR] Full error response: {error_data}")
            raise Exception(f"Gemini API Error: {error_msg}")
        
        data = response.json()
        print("[OK] API Response received")
        
        # Extract text from response
        if not data.get("candidates") or not data["candidates"][0].get("content"):
            print(f"[ERROR] Invalid response structure: {data}")
            raise Exception("Invalid response structure from Gemini API")
        
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"[INFO] AI Response Text:\n{ai_text}")
        
        # Clean and parse JSON
        json_text = ai_text.strip()
        
        # Remove markdown code blocks if present
        if json_text.startswith("```"):
            json_text = json_text.split("```")[1]
            if json_text.startswith("json"):
                json_text = json_text[4:]
        
        json_text = json_text.strip()
        
        print("[INFO] Parsing JSON response...")
        parsed_data = json.loads(json_text)
        print("[OK] JSON parsed successfully")
        print(f"[INFO] Extracted Data: {json.dumps(parsed_data, indent=2)}")
        
        # Convert to StudentProfile
        marks = []
        for subject_data in parsed_data.get("subjects", []):
            mark = SubjectMark(
                subject=subject_data["subject"],
                score=float(subject_data["score"]),
                max_score=float(subject_data.get("maxScore", 100))
            )
            marks.append(mark)
        
        # Determine region (default to "India" if not specified)
        region = parsed_data.get("region", "India")
        
        # Map category
        category_str = parsed_data.get("category", "General")
        if category_str == "Not Mentioned":
            category_str = "General"
        
        # Create student profile
        profile = StudentProfile(
            name=parsed_data.get("name", "Unknown Student"),
            region=region,
            overall_percentage=float(parsed_data.get("percentage", 0)),
            marks=marks,
            income_level=parsed_data.get("incomeLevel", "Not Mentioned"),
            category=category_str if category_str != "Not Mentioned" else None,
            parent_occupation=parsed_data.get("parentOccupation") if parsed_data.get("parentOccupation") != "Not Mentioned" else None,
            extraction_method="AI"
        )
        
        print(f"[OK] Successfully created student profile for: {profile.name}")
        return profile
        
    except httpx.TimeoutException:
        print("[ERROR] Request timeout")
        raise Exception("Gemini API request timed out")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}")
        print(f"[ERROR] Raw text: {ai_text if 'ai_text' in locals() else 'N/A'}")
        raise Exception(f"Failed to parse AI response as JSON: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        raise


def parse_marksheet_with_ai_sync(ocr_text: str) -> StudentProfile:
    """Synchronous wrapper for parse_marksheet_with_ai"""
    import asyncio
    return asyncio.run(parse_marksheet_with_ai(ocr_text))


async def parse_marksheet_image_with_vision(image_path: str) -> StudentProfile:
    """
    Directly analyze a marksheet image using Gemini Vision API.
    This is used when OCR is not available (Tesseract not installed).
    """
    import base64
    import mimetypes
    
    print(f"[INFO] Using Gemini Vision API to analyze image: {image_path}")
    
    # Read and encode the image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    
    # Determine MIME type
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        # Default based on extension
        ext = image_path.lower().split('.')[-1]
        mime_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'pdf': 'application/pdf'
        }
        mime_type = mime_map.get(ext, 'image/jpeg')
    
    print(f"[INFO] Image MIME type: {mime_type}")
    
    # Prompt for vision-based extraction - works with ANY marksheet format
    prompt = """You are an expert at reading and extracting data from academic marksheets, transcripts, and grade cards from ANY educational board or institution worldwide.

Analyze this marksheet/transcript/grade card image carefully and extract ALL visible information.

IMPORTANT: This could be from ANY board/university such as:
- Indian State Boards (Tamil Nadu, Karnataka, Maharashtra, Kerala, AP, Telangana, UP, Bihar, etc.)
- CBSE, ICSE, ISC
- State Universities
- International boards (IB, Cambridge, etc.)
- College/University transcripts
- Semester marksheets
- Any other academic document

Extract and return a JSON object with EXACTLY this structure:
{
    "name": "Student's full name as shown in document",
    "rollNumber": "Roll number/Registration number if visible",
    "board": "Board/University name (e.g., Tamil Nadu State Board, CBSE, Mumbai University)",
    "examName": "Examination name (e.g., SSLC, HSC, 10th, 12th, Semester 1)",
    "year": "Year of examination",
    "percentage": 85.5,
    "totalMarks": 425,
    "maxMarks": 500,
    "grade": "Grade if mentioned (A+, A, B, etc.)",
    "subjects": [
        {"name": "Subject Name", "score": 85, "maxScore": 100, "grade": "A"}
    ],
    "region": "State/Country (e.g., Tamil Nadu, Karnataka, India)",
    "schoolName": "School/College name if visible",
    "incomeLevel": "Not Mentioned",
    "category": "General/OBC/SC/ST/EWS or Not Mentioned",
    "parentOccupation": "Not Mentioned",
    "dateOfBirth": "DOB if visible in YYYY-MM-DD format",
    "fatherName": "Father's name if visible",
    "motherName": "Mother's name if visible"
}

CRITICAL INSTRUCTIONS:
1. Extract EVERY subject with marks visible in the image
2. Calculate overall percentage: (total obtained marks / total maximum marks) * 100
3. Look for marks in various formats: 85/100, 85 out of 100, 85 (100), Grade A = 90, etc.
4. Handle both numeric scores and letter grades
5. If maximum marks per subject is not shown, assume 100
6. Use "Not Mentioned" for fields not visible in the document
7. Be thorough - extract ALL subjects even if there are many
8. Return ONLY valid JSON, no other text or explanation"""

    # Use Gemini 2.0 Flash for vision (supports multimodal) - v1beta API
    vision_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": image_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 2048
        }
    }
    
    # Retry logic with exponential backoff for rate limiting
    max_retries = 3
    base_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{vision_url}?key={GEMINI_API_KEY}",
                    headers=headers,
                    json=payload
                )
                
                print(f"[INFO] Vision API Response Status: {response.status_code}")
                
                if response.status_code == 429:
                    # Rate limited - wait and retry
                    delay = base_delay * (2 ** attempt)
                    print(f"[WAIT] Rate limited (429). Waiting {delay}s before retry {attempt + 1}/{max_retries}...")
                    await asyncio.sleep(delay)
                    continue
                
                if response.status_code != 200:
                    print(f"[ERROR] API Error: {response.text}")
                    raise Exception(f"Gemini Vision API error: {response.status_code}")
                
                result = response.json()
            
            # Extract text from response
            ai_text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"[INFO] Vision AI Response:\n{ai_text[:500]}...")
            
            # Clean and parse JSON
            ai_text = ai_text.strip()
            if ai_text.startswith("```json"):
                ai_text = ai_text[7:]
            if ai_text.startswith("```"):
                ai_text = ai_text[3:]
            if ai_text.endswith("```"):
                ai_text = ai_text[:-3]
            ai_text = ai_text.strip()
            
            parsed_data = json.loads(ai_text)
            
            # Build marks list
            marks = []
            for subject_data in parsed_data.get("subjects", []):
                mark = SubjectMark(
                    subject=subject_data.get("name", "Unknown"),
                    score=float(subject_data.get("score", 0)),
                    max_score=float(subject_data.get("maxScore", 100))
                )
                marks.append(mark)
            
            # Map category
            category_str = parsed_data.get("category", "General")
            if category_str == "Not Mentioned":
                category_str = "General"
            
            # Calculate percentage if not provided but we have total marks
            percentage = parsed_data.get("percentage", 0)
            if percentage == 0 and parsed_data.get("totalMarks") and parsed_data.get("maxMarks"):
                percentage = (float(parsed_data.get("totalMarks")) / float(parsed_data.get("maxMarks"))) * 100
            
            # If still no percentage, calculate from subjects
            if percentage == 0 and marks:
                total_score = sum(m.score for m in marks)
                total_max = sum(m.max_score for m in marks)
                if total_max > 0:
                    percentage = (total_score / total_max) * 100
            
            # Determine region from board name if not specified
            region = parsed_data.get("region", "India")
            board = parsed_data.get("board", "")
            if region == "India" and board:
                # Try to extract state from board name
                state_keywords = {
                    "tamil nadu": "Tamil Nadu", "tn": "Tamil Nadu",
                    "karnataka": "Karnataka", "ka": "Karnataka",
                    "maharashtra": "Maharashtra", "mh": "Maharashtra",
                    "kerala": "Kerala", "kl": "Kerala",
                    "andhra": "Andhra Pradesh", "ap": "Andhra Pradesh",
                    "telangana": "Telangana", "ts": "Telangana",
                    "west bengal": "West Bengal", "wb": "West Bengal",
                    "uttar pradesh": "Uttar Pradesh", "up": "Uttar Pradesh",
                    "bihar": "Bihar", "rajasthan": "Rajasthan",
                    "gujarat": "Gujarat", "punjab": "Punjab",
                    "cbse": "India (CBSE)", "icse": "India (ICSE)",
                    "isc": "India (ISC)"
                }
                board_lower = board.lower()
                for keyword, state in state_keywords.items():
                    if keyword in board_lower:
                        region = state
                        break
            
            # Create student profile with all extracted data
            profile = StudentProfile(
                name=parsed_data.get("name", "Unknown Student"),
                region=region,
                overall_percentage=float(percentage),
                marks=marks,
                income_level=parsed_data.get("incomeLevel", "Not Mentioned"),
                category=category_str if category_str != "Not Mentioned" else None,
                parent_occupation=parsed_data.get("parentOccupation") if parsed_data.get("parentOccupation") != "Not Mentioned" else None,
                education_level=parsed_data.get("examName", parsed_data.get("board", "Not Mentioned")),
                date_of_birth=parsed_data.get("dateOfBirth") if parsed_data.get("dateOfBirth") != "Not Mentioned" else None,
                extraction_method="AI_Vision"
            )
            
            # Log extracted details
            print(f"[OK] Vision extraction successful!")
            print(f"   Name: {profile.name}")
            print(f"   Board: {board}")
            print(f"   Percentage: {profile.overall_percentage:.2f}%")
            print(f"   Subjects: {len(marks)}")
            print(f"   Region: {region}")
            
            return profile
            
        except httpx.TimeoutException:
            print("[ERROR] Vision API timeout")
            raise Exception("Gemini Vision API request timed out")
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parsing error: {e}")
            raise Exception(f"Failed to parse Vision API response: {e}")
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"[WAIT] Rate limit error. Waiting {delay}s...")
                await asyncio.sleep(delay)
                continue
            print(f"[ERROR] Vision API error: {e}")
            raise
    
    # If all retries exhausted
    raise Exception("Gemini Vision API rate limit exceeded. Please try again later.")
