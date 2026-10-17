import cv2
import mediapipe as mp
import time
import math
import pygame
import numpy as np

MODEL_PATH = r"D:\Projects\emotion-soundboard\mediapipe_finger\models\hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

def distance(a, b):
    return math.sqrt(
        (a.x - b.x) ** 2 +
        (a.y - b.y) ** 2 +
        (a.z - b.z) ** 2
    )


# def finger_extended(landmarks, pip_id, tip_id):
#     wrist = landmarks[0]

#     pip = landmarks[pip_id]
#     tip = landmarks[tip_id]

#     pip_distance = distance(wrist, pip)
#     tip_distance = distance(wrist, tip)

#     return tip_distance > pip_distance

def joint_angle(a, b, c):
    ba = np.array([
        a.x - b.x,
        a.y - b.y,
        a.z - b.z
    ])

    bc = np.array([
        c.x - b.x,
        c.y - b.y,
        c.z - b.z
    ])

    cosine = np.dot(ba, bc) / (
        np.linalg.norm(ba) * np.linalg.norm(bc)
    )

    return np.degrees(
        np.arccos(np.clip(cosine, -1.0, 1.0))
    )

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

pygame.mixer.init()
middle_finger_sound = pygame.mixer.Sound("FU.mp3")

landmarker = HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

start_time = time.time()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # OpenCV gives us BGR
    # MediaPipe expects RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp_ms = int((time.time() - start_time) * 1000)

    result = landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )

    height, width, _ = frame.shape

    FINGER_UP_THRESHOLD = 155

    if result.hand_landmarks:

        for hand in result.hand_landmarks:

            index_angle = joint_angle(hand[5], hand[6], hand[8])
            middle_angle = joint_angle(hand[9], hand[10], hand[12])
            ring_angle = joint_angle(hand[13], hand[14], hand[16])
            pinky_angle = joint_angle(hand[17], hand[18], hand[20])

            index_up = index_angle > FINGER_UP_THRESHOLD
            middle_up = middle_angle > FINGER_UP_THRESHOLD
            ring_up = ring_angle > FINGER_UP_THRESHOLD
            pinky_up = pinky_angle > FINGER_UP_THRESHOLD

            middle_finger_gesture = (
                    not index_up and
                    middle_up and
                    not ring_up and
                    not pinky_up
                )
            
            positive = "Fuck you"
            negative = "UwU"

            if middle_finger_gesture:
                status = positive
                middle_finger_sound.play()
            else:
                status = negative

            # print(
            #     f"INDEX: {index_up} | "
            #     f"MIDDLE: {middle_up} | "
            #     f"RING: {ring_up} | "
            #     f"PINKY: {pinky_up}"
            # )
            
            # status = (
            #     f"I:{index_up} "
            #     f"M:{middle_up} "
            #     f"R:{ring_up} "
            #     f"P:{pinky_up}"
            # )
            
            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )

            

            # index_up = finger_extended(hand, 6, 8)
            # middle_up = finger_extended(hand, 10, 12)
            # ring_up = finger_extended(hand, 14, 16)
            # pinky_up = finger_extended(hand, 18, 20)

            # status = (
            #     f"INDEX:{index_up}  "
            #     f"MIDDLE:{middle_up}  "
            #     f"RING:{ring_up}  "
            #     f"PINKY:{pinky_up}"
            # )

            

            # Draw each of the 21 landmark points
            for landmark_id, landmark in enumerate(hand):

                x = int(landmark.x * width)
                y = int(landmark.y * height)

                cv2.circle(
                    frame,
                    (x, y),
                    5,
                    (255, 255, 255),
                    -1
                )

                cv2.putText(
                    frame,
                    str(landmark_id),
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )


    cv2.imshow("MediaPipe Hand Test", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cap.release()
landmarker.close()
cv2.destroyAllWindows()