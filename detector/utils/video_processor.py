import cv2
import numpy as np

def extract_best_frames(video_path, frame_count=10):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = []
    if total_frames > 0:
        interval = total_frames // frame_count
        for i in range(frame_count):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i * interval)
            success, frame = cap.read()
            if success:
                processed = cv2.resize(frame, (224, 224)).astype('float32') / 255.0
                frames.append(processed)
    cap.release()
    meta = {"duration": round(total_frames/fps, 2) if fps > 0 else 0, "res": f"{int(cap.get(3))}x{int(cap.get(4))}"}
    return np.array(frames), meta