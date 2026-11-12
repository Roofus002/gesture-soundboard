
import time


def is_fist(hand):
    """Check whether all four fingers are curled."""

    return (
        not hand.index_up
        and not hand.middle_up
        and not hand.ring_up
        and not hand.pinky_up
    )


class FistShakeTracker:
    """
    Detect a fist moving right-left-right
    or left-right-left.
    """

    MIN_TRAVEL = 0.045
    MAX_DURATION = 3.0
    MAX_FRAME_GAP = 0.6
    COOLDOWN = 1.5
    
    def __init__(self):
        self.cooldown_until = 0.0
        self.reset()

    def reset(self):
        self.anchor_x = None
        self.extreme_x = None
        self.last_x = None
        self.direction = 0
        self.reversals = 0
        self.started_at = None
        self.last_seen_at = None

    def update(self, hands, now=None):
        if now is None:
            now = time.monotonic()

        # Find all closed fists in this frame.
        fists = [
            hand for hand in hands
            if is_fist(hand)
        ]

        if not fists:

            # Allow brief tracking interruptions.
            # MediaPipe may miss a fist during fast movement.
            if (
                self.last_seen_at is not None
                and now - self.last_seen_at <= 0.35
            ):
                return False

            self.reset()
            return False

        # Track the fist nearest its previous position.
        fist = (
            min(
                fists,
                key=lambda hand: abs(
                    hand.wrist_x - self.last_x
                )
            )
            if self.last_x is not None
            else fists[0]
        )

        x = fist.wrist_x

        if now < self.cooldown_until:
            self.reset()
            return False

        # Expire interrupted or slow movements.
        if (
            self.last_seen_at is not None
            and now - self.last_seen_at > self.MAX_FRAME_GAP
        ) or (
            self.started_at is not None
            and now - self.started_at > self.MAX_DURATION
        ):
            self.reset()

        self.last_seen_at = now
        self.last_x = x

        if self.anchor_x is None:
            self.anchor_x = x
            self.started_at = now
            return False

        # Detect initial direction.
        if self.direction == 0:
            movement = x - self.anchor_x

            if abs(movement) >= self.MIN_TRAVEL:
                self.direction = (
                    1 if movement > 0 else -1
                )
                self.extreme_x = x

            return False

        # Detect a reversal from right to left.
        if self.direction == 1:
            if x > self.extreme_x:
                self.extreme_x = x

            elif self.extreme_x - x >= self.MIN_TRAVEL:
                self.direction = -1
                self.extreme_x = x
                self.reversals += 1

        # Detect a reversal from left to right.
        else:
            if x < self.extreme_x:
                self.extreme_x = x

            elif x - self.extreme_x >= self.MIN_TRAVEL:
                self.direction = 1
                self.extreme_x = x
                self.reversals += 1

        if self.reversals >= 2:
            self.cooldown_until = now + self.COOLDOWN
            self.reset()
            return True

        return False
