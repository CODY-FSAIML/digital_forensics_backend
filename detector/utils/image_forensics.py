try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Adjust path as needed
except ImportError:
    pytesseract = None

from PIL import Image, ImageChops
import os


def perform_ela(image_path, quality=90):
    original = Image.open(image_path).convert('RGB')
    temp_path = 'temp_ela.jpg'
    original.save(temp_path, 'JPEG', quality=quality)
    resaved = Image.open(temp_path)
    ela_diff = ImageChops.difference(original, resaved)
    extrema = ela_diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if os.path.exists(temp_path): os.remove(temp_path)
    return max_diff, ela_diff

def analyze_screenshot_content(image_path):
    if pytesseract is None:
        # OCR not installed; return empty results so callers can proceed
        return "", []

    text = pytesseract.image_to_string(Image.open(image_path))
    scams = [w for w in ['winner', 'blocked', 'urgent', 'verify'] if w in text.lower()]
    return text, scams