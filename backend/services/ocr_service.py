"""
OCR Service for extracting text from images and PDFs
Uses Tesseract OCR or falls back to basic extraction
"""

import os
from typing import Optional
from PIL import Image

# Try importing pytesseract - it may not be available
try:
    import pytesseract
    
    # Configure Tesseract path for Windows
    # Download from: https://github.com/UB-Mannheim/tesseract/wiki
    TESSERACT_PATHS = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
    ]
    
    tesseract_found = False
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tesseract_found = True
            print(f"[OK] Tesseract found at: {path}")
            break
    
    if not tesseract_found:
        # Check if in PATH
        import shutil
        if shutil.which("tesseract"):
            tesseract_found = True
            print("[OK] Tesseract found in PATH")
    
    TESSERACT_AVAILABLE = tesseract_found
    if not tesseract_found:
        print("[WARN] Tesseract not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        
except ImportError:
    TESSERACT_AVAILABLE = False
    print("[WARN] pytesseract not installed - will use AI-based extraction")

# Try importing pdf2image - it may not be available
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("[WARN] pdf2image not available - PDF processing limited")


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image file using Tesseract OCR
    Falls back to returning placeholder if Tesseract is not available
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        print(f"[INFO] Opening image: {image_path}")
        image = Image.open(image_path)
        
        if TESSERACT_AVAILABLE:
            print("[INFO] Performing OCR with Tesseract...")
            try:
                text = pytesseract.image_to_string(image, lang='eng')
                print(f"[OK] Extracted {len(text)} characters")
                return text.strip()
            except Exception as e:
                print(f"[WARN] Tesseract OCR failed: {e}")
                # Fall through to AI-based extraction
        
        # Return image info for AI processing
        print("[INFO] Using AI-based extraction (no Tesseract)")
        width, height = image.size
        return f"[IMAGE_FILE: {os.path.basename(image_path)}, size: {width}x{height}. Use AI vision for extraction.]"
        
    except Exception as e:
        print(f"[ERROR] Error processing image: {e}")
        raise Exception(f"Image processing failed: {e}")


def extract_text_from_pdf(pdf_path: str, dpi: int = 300) -> str:
    """
    Extract text from a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for image conversion (higher = better quality but slower)
        
    Returns:
        Extracted text from all pages
    """
    try:
        if not PDF2IMAGE_AVAILABLE:
            print("[WARN] pdf2image not available - returning placeholder for AI extraction")
            return f"[PDF_FILE: {os.path.basename(pdf_path)}. Use AI vision for extraction.]"
        
        print(f"[INFO] Converting PDF to images: {pdf_path}")
        
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        print(f"[INFO] Processing {len(images)} pages...")
        
        all_text = []
        for i, image in enumerate(images, 1):
            print(f"[INFO] OCR on page {i}/{len(images)}...")
            if TESSERACT_AVAILABLE:
                page_text = pytesseract.image_to_string(image, lang='eng')
            else:
                page_text = f"[Page {i} - use AI vision for extraction]"
            all_text.append(page_text)
        
        combined_text = "\n\n".join(all_text)
        print(f"[OK] Extracted {len(combined_text)} characters from PDF")
        
        return combined_text.strip()
        
    except Exception as e:
        print(f"[ERROR] Error extracting text from PDF: {e}")
        raise Exception(f"PDF OCR failed: {e}")


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from image or PDF file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.webp', '.gif', '.webp', '.gif']:
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def preprocess_image(image_path: str, output_path: Optional[str] = None) -> str:
    """
    Preprocess image for better OCR results
    
    Args:
        image_path: Path to input image
        output_path: Optional path for output (if None, overwrites input)
        
    Returns:
        Path to preprocessed image
    """
    try:
        from PIL import ImageEnhance, ImageFilter
        
        image = Image.open(image_path)
        
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Sharpen
        image = image.filter(ImageFilter.SHARPEN)
        
        # Save
        save_path = output_path or image_path
        image.save(save_path)
        
        print(f"[OK] Preprocessed image saved to: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"[WARN] Warning: Image preprocessing failed: {e}")
        return image_path
