import cv2
import mediapipe as mp
from pathlib import Path

from hand_features import extract_features
from gestures.middle_finger import is_middle_finger


MODEL_PATH = (
    Path(__file__).resolve().parent
    / ".."
    / ".."
    / "models"
    / "hand_landmarker.task"
).resolve()


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



def extract_hands(frame):
    """
    Run MediaPipe once and return features
    for every detected hand.
    """

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    result = landmarker.detect(mp_image)

    hands = []

    for hand in result.hand_landmarks:
        features = extract_features(hand)
        hands.append(features)

    return hands


def detect_middle_finger(frame):
    """
    Temporary compatibility function for app.py.
    """

    hands = extract_hands(frame)

    for hand in hands:

        if is_middle_finger(
            index_up=hand.index_up,
            middle_up=hand.middle_up,
            ring_up=hand.ring_up,
            pinky_up=hand.pinky_up
        ):
            return True

    return False
