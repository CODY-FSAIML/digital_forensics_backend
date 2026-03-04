import cv2
import numpy as np

def analyze_video_realness(video_path):
    """
    Real Computer Vision analysis! 
    Reads video frames and checks for deepfake artifacts like 
    unnatural blur (Laplacian variance) and frame-to-frame glitches.
    """
    cap = cv2.VideoCapture(video_path)
    blur_scores = []
    frame_diffs = []
    
    ret, prev_frame = cap.read()
    if not ret:
        return 0.0, ["Error reading video frames."]
        
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_count = 1

    # Analyze up to 60 frames (2 seconds) for speed
    while cap.isOpened() and frame_count < 60:
        ret, frame = cap.read()
        if not ret:
            break
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Check for unnatural facial smoothing/blur
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_scores.append(blur_score)
        
        # 2. Check for micro-glitches between frames (frame differencing)
        diff = cv2.absdiff(gray, prev_gray)
        frame_diffs.append(np.mean(diff))
        
        prev_gray = gray
        frame_count += 1
        
    cap.release()
    
    # --- The AI Math ---
    fake_probability = 0.0
    reasons = []
    
    avg_blur = np.mean(blur_scores) if blur_scores else 0
    glitch_variance = np.var(frame_diffs) if frame_diffs else 0
    
    # Deepfakes often have highly inconsistent blur (faces pop in and out of focus)
    if np.var(blur_scores) > 300:
        fake_probability += 0.45
        reasons.append(f"Inconsistent spatial frequency detected (Variance: {np.var(blur_scores):.1f}).")
    else:
        reasons.append("Spatial frequency is natural and consistent.")
        
    # Deepfakes often have high micro-glitches between frames
    if glitch_variance > 10.0:
        fake_probability += 0.45
        reasons.append(f"High inter-frame glitch variance detected ({glitch_variance:.1f}).")
    else:
        reasons.append("Smooth temporal transitions detected.")
        
    # Cap the probability between 0% and 99%
    final_score = min(max(fake_probability, 0.05), 0.99)
    
    return final_score, reasons