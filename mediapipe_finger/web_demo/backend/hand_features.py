from dataclasses import dataclass
import numpy as np


FINGER_UP_THRESHOLD = 155


@dataclass
class HandFeatures:
    index_up: bool
    middle_up: bool
    ring_up: bool
    pinky_up: bool

    wrist_x: float
    wrist_y: float

    landmarks: object


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

    denominator = (
        np.linalg.norm(ba)
        * np.linalg.norm(bc)
    )

    if denominator < 1e-8:
        return 0.0

    cosine = np.dot(ba, bc) / denominator

    return np.degrees(
        np.arccos(np.clip(cosine, -1.0, 1.0))
    )


def extract_features(hand):

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

    return HandFeatures(
        index_up=index_angle > FINGER_UP_THRESHOLD,
        middle_up=middle_angle > FINGER_UP_THRESHOLD,
        ring_up=ring_angle > FINGER_UP_THRESHOLD,
        pinky_up=pinky_angle > FINGER_UP_THRESHOLD,

        wrist_x=hand[0].x,
        wrist_y=hand[0].y,

        landmarks=hand
    )