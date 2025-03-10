import cv2
import numpy as np
import time
import os

def detect_eye_contact_ratio_continuous_haar(video_source, interval=5):
    """
    Detects eye contact ratio every 'interval' seconds continuously using Haar Cascades.
    """

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

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
            all_eyes_detected = []

            while time.time() - start_time < interval and running:
                ret, frame = cap.read()
                if not ret:
                    if isinstance(video_source, str) and os.path.exists(video_source):
                        running = False
                        break
                    else:
                        break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y + h, x:x + w]
                    roi_color = frame[y:y + h, x:x + w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)

                    if len(eyes) >= 2: # Check if at least two eyes are detected
                        eye_contact_frames +=1
                        all_eyes_detected.append(True)
                    else:
                        all_eyes_detected.append(False)

                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                total_frames += 1

                cv2.imshow("Eye Contact Detection", frame)
                if cv2.waitKey(1) & 0xFF == ord(' '):
                    running = False
                    break

            if total_frames > 0 and running:
                eye_contact_ratio = (eye_contact_frames / total_frames) * 100
                print(f"Eye contact ratio over {interval} seconds: {eye_contact_ratio:.2f}%")
                all_ratios.append(eye_contact_ratio)

                if all_eyes_detected:
                    eyes_detected_ratio = sum(all_eyes_detected)/len(all_eyes_detected)
                    print(f"Percentage of frames with eyes detected: {eyes_detected_ratio*100:.2f}%")

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

if __name__ == "__main__":
    video_input = input("Enter video source (0 for webcam, or video file path): ")
    try:
        video_source = int(video_input)
    except ValueError:
        video_source = video_input

    detect_eye_contact_ratio_continuous_haar(video_source, interval=5)