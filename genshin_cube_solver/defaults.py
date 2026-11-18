"""Default puzzle used by the command line and web interfaces."""

from copy import deepcopy

INITIAL_STATE = "2 1 1 3"
ATTACK_MAP = {
    1: [1, 2],
    2: [2, 3, 1],
    3: [3, 2, 4],
    4: [4, 3],
}
MAX_STEPS = 10


def get_default_config() -> dict:
    return {
        "initial": INITIAL_STATE,
        "attack_map": deepcopy(ATTACK_MAP),
        "max_steps": MAX_STEPS,
    }
