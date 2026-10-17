import cv2
import math
import numpy as np
import mediapipe as mp
from pathlib import Path


MODEL_PATH = (
    Path(__file__).resolve().parent
    / ".."
    / ".."
    / "models"
    / "hand_landmarker.task"
).resolve()

FINGER_UP_THRESHOLD = 155


BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=str(MODEL_PATH)
    ),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=2
)

landmarker = HandLandmarker.create_from_options(options)


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


def detect_middle_finger(frame):

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    result = landmarker.detect(mp_image)

    if not result.hand_landmarks:
        return False

    for hand in result.hand_landmarks:

        index_angle = joint_angle(
            hand[5], hand[6], hand[8]
        )

        middle_angle = joint_angle(
            hand[9], hand[10], hand[12]
        )

        ring_angle = joint_angle(
            hand[13], hand[14], hand[16]
        )

        pinky_angle = joint_angle(
            hand[17], hand[18], hand[20]
        )

        index_up = index_angle > FINGER_UP_THRESHOLD
        middle_up = middle_angle > FINGER_UP_THRESHOLD
        ring_up = ring_angle > FINGER_UP_THRESHOLD
        pinky_up = pinky_angle > FINGER_UP_THRESHOLD

        middle_finger_gesture = (
            not index_up
            and middle_up
            and not ring_up
            and not pinky_up
        )

        if middle_finger_gesture:
            return True

    return False