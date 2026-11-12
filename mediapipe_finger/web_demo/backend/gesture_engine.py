
from hand_detector import extract_hands

from gestures.middle_finger import is_middle_finger
from gestures.fist_shake import FistShakeTracker, is_fist


def check_middle_finger(hands):

    for hand in hands:
        if is_middle_finger(
            index_up=hand.index_up,
            middle_up=hand.middle_up,
            ring_up=hand.ring_up,
            pinky_up=hand.pinky_up
        ):
            return True

    return False


# Static gestures checked by priority.
STATIC_GESTURES = [
    ("middle_finger", check_middle_finger),
]


class GestureEngine:

    def __init__(self):
        self.fist_tracker = FistShakeTracker()

    def process(self, frame):

        # Run MediaPipe once per frame.
        hands = extract_hands(frame)


        # Check static gestures first.
        for gesture_name, recogniser in STATIC_GESTURES:

            if recogniser(hands):
                self.fist_tracker.reset()
                return gesture_name

        # Identify a closed fist.
        fist_detected = any(
            is_fist(hand) for hand in hands
        )

        # Detect horizontal fist movement.
        if self.fist_tracker.update(hands):
            return "fist_shake"

        # Debugging: fist detected but not shaking.
        if fist_detected:
            return "fist"

        return "normal"
