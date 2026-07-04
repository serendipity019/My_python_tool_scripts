import os
from cv2 import (
    imread,
    COLOR_BGR2GRAY,
    countNonZero,
    CV_64F,
    cvtColor,
    Laplacian,
    inRange)
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
file_path = os.getenv("FILE_PATH")
print(file_path)

def analyze_photo_quality(jpg_path: Path, blur_threshold: int = 100, exposure_threshold : float  = 0.85) -> str:
    """
    Analyzes a JPG image for blur and extreme exposure.
    Returns: 'blurry', 'overexposed', 'underexposed', or 'good'
    """
    # Load the image using OpenCV
    # (I use imread, which handles reading the pixel matrix)
    img = imread(str(jpg_path))
    if img is None:
        return "error"
    
    # 1. BLUR DETECTION (Laplacian Variance) for shake photos or slower shutter than needed.
    # Convert to grayscale because edge detection doesn't need color
    gray = cvtColor(img, COLOR_BGR2GRAY)
    # Calculate the focus measure (higher means sharper, lower means blurrier)
    focus_measure = Laplacian(gray, CV_64F).var()

    if focus_measure < blur_threshold:
        return "blurry"
    
    # 2. EXPOSURE DETECTION (Histogram Analysis)
    # Calculate how many pixels are completely black (0) or completely white (255)
    total_pixels = gray.size

    # Count pure white pixels (value 240 to 255) for burned images
    white_pixels = countNonZero(inRange(gray, 240, 255))
    # Count black pixels (value 0 to 15) for pitch black images
    black_pixels = countNonZero(inRange(gray, 0, 15))

    # If a massive percentage of the photo is pure white or pure dark
    if (white_pixels / total_pixels) > exposure_threshold:
        return "overexposed"
    if (black_pixels / total_pixels) > exposure_threshold:
        return "underexposed"
    
    return "good"

# --- Quick Test ---
# Point this to ONE of your bad test JPG photos to see what it detects
test_file = Path(file_path)
if test_file.exists():
    result = analyze_photo_quality(test_file)
    print(f"Analysis result for {test_file.name}: {result}")
