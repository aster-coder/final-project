"""
    How this function works:
    Takes the video source, stored in the temp videos folder and an interval of 5 seconds
    Uses Histogram of Oriented Gradients for eye contact detection
    takes the shape landmarks file for the reference, and dlibs frontal face detector
    Calcuates the Eye Aspect Ratio(EAR) for each frame and predicts the landmarks for the eyes
    debug prints the current eye contact ratio over the interval
    returns the average eye contact ratio in percentage format
"""
#imports
import cv2
import dlib
import numpy as np
import time
import os

def detect_eye_contact_ratio(video_source, interval=5):
    if not isinstance(video_source, str) or not os.path.exists(video_source):
        print("Error: Invalid video file path.")
        return None
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return None
    all_ratios = []
    running = True
    try:
        while running:
            start_time = time.time()
            eye_contact_frames = 0
            total_frames = 0
            while time.time() - start_time < interval and running:
                ret, frame = cap.read()
                if not ret:
                    running = False
                    break
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)
                for face in faces:
                    landmarks = predictor(gray, face)
                    left_eye_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(36, 42)]
                    right_eye_points = [(landmarks.part(n).x, landmarks.part(n).y) for n in range(42, 48)]
                    left_ear = calculate_ear(left_eye_points)
                    right_ear = calculate_ear(right_eye_points)
                    ear = (left_ear + right_ear) / 2.0
                    if ear > 0.2:
                        eye_contact_frames += 1
                total_frames += 1
            if total_frames > 0 and running:
                eye_contact_ratio = (eye_contact_frames / total_frames) * 100
                all_ratios.append(eye_contact_ratio)
                #print(f"Eye contact ratio over {interval} seconds: {eye_contact_ratio:.2f}%") #Debug print
            elif not running:
                break
            else:
                print("No frames processed during the interval.")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        cap.release()
    if all_ratios:
        average_eye_contact = sum(all_ratios) / len(all_ratios)
        return average_eye_contact
    else:
        return 0.0

def calculate_ear(eye_points):
    """Calculates the Eye Aspect Ratio (EAR)."""
    A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    ear = (A + B) / (2.0 * C)
    return ear

if __name__ == "__main__":
    video_input = input("Enter video file path: ")

    average_ratio = detect_eye_contact_ratio(video_input, interval=5)

    if average_ratio is not None:
        print(f"Overall average eye contact ratio: {average_ratio:.2f}%")