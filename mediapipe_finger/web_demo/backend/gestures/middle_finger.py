
def is_middle_finger(
    *,
    index_up: bool,
    middle_up: bool,
    ring_up: bool,
    pinky_up: bool
) -> bool:

    return (
        not index_up
        and middle_up
        and not ring_up
        and not pinky_up
    )
