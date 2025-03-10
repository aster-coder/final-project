import cv2
import dlib
import numpy as np
import time
import os

def detect_eye_contact_ratio_continuous(video_source, interval=5):
    """
    Detects eye contact ratio every 'interval' seconds continuously and calculates the overall average.

    Args:
        video_source (int or str): The video source (webcam or video file path).
        interval (int): The interval in seconds.
    """

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    all_ratios = []
    running = True

    try:
        while running:
            start_time = time.time()
            eye_contact_frames = 0
            total_frames = 0
            all_ears = []

            while time.time() - start_time < interval and running:
                ret, frame = cap.read()
                if not ret:
                    if isinstance(video_source, str) and os.path.exists(video_source):
                        running = False
                        break
                    else:
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
                    all_ears.append(ear)

                    if ear > 0.2:
                        eye_contact_frames += 1

                    for n in range(36, 48):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                total_frames += 1

                cv2.imshow("Eye Contact Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    running = False
                    break

            if total_frames > 0 and running:
                eye_contact_ratio = (eye_contact_frames / total_frames) * 100
                print(f"Eye contact ratio over {interval} seconds: {eye_contact_ratio:.2f}%")
                all_ratios.append(eye_contact_ratio)

                if all_ears:
                    average_ear = sum(all_ears) / len(all_ears)
                    min_ear = min(all_ears)
                    max_ear = max(all_ears)
                    print(f"Average EAR: {average_ear:.4f}, Min EAR: {min_ear:.4f}, Max EAR: {max_ear:.4f}")
            elif not running:
                break
            else:
                print("No frames processed during the interval.")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

        if all_ratios:
            average_eye_contact = sum(all_ratios) / len(all_ratios)
            print(f"\nOverall average eye contact ratio: {average_eye_contact:.2f}%")
        else:
            print("\nNo eye contact ratios recorded.")

def calculate_ear(eye_points):
    """Calculates the Eye Aspect Ratio (EAR)."""
    A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    ear = (A + B) / (2.0 * C)
    return ear

if __name__ == "__main__":
    video_input = input("Enter video source (0 for webcam, or video file path): ")
    try:
        video_source = int(video_input)
    except ValueError:
        video_source = video_input

    detect_eye_contact_ratio_continuous(video_source, interval=5)