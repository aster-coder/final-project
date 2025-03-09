import cv2
import dlib
import numpy as np
import time

def detect_eye_contact_ratio_continuous(video_source=0, interval=5):
    """
    Detects eye contact ratio every 'interval' seconds continuously.

    Args:
        video_source (int or str): The video source.
        interval (int): The interval in seconds.
    """

    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    try:
        while True:
            start_time = time.time()
            eye_contact_frames = 0
            total_frames = 0

            while time.time() - start_time < interval:
                ret, frame = cap.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = detector(gray)

                for face in faces:
                    landmarks = predictor(gray, face)
                    left_eye_points = []
                    right_eye_points = []

                    for n in range(36, 42):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        left_eye_points.append((x, y))
                    for n in range(42, 48):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        right_eye_points.append((x, y))

                    left_ear = calculate_ear(left_eye_points)
                    right_ear = calculate_ear(right_eye_points)
                    ear = (left_ear + right_ear) / 2.0

                    if ear > 0.2:  # Adjust threshold as needed
                        eye_contact_frames += 1

                total_frames += 1

                # Display with landmarks
                for face in faces:
                    landmarks = predictor(gray, face)
                    for n in range(36, 48):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

                cv2.imshow("Eye Contact Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord(' '): #press space to pause
                    return # Exit the function, ending the program.

            if total_frames > 0:
                eye_contact_ratio = (eye_contact_frames / total_frames) * 100
                print(f"Eye contact ratio over {interval} seconds: {eye_contact_ratio:.2f}%")
            else:
                print("No frames processed during the interval.")

    except KeyboardInterrupt: # Handle CTRL+C
        print("\nProgram interrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()

def calculate_ear(eye_points):
    """Calculates the Eye Aspect Ratio (EAR)."""
    A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
    B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
    C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
    ear = (A + B) / (2.0 * C)
    return ear

if __name__ == "__main__":
    detect_eye_contact_ratio_continuous(interval=1)