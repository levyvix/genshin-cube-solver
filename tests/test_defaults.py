from app.app import DEFAULT_CONFIG
from genshin_cube_solver.defaults import ATTACK_MAP, INITIAL_STATE, MAX_STEPS, get_default_config
from main import ATTACK_MAP as CLI_ATTACK_MAP, INITIAL_STATE as CLI_INITIAL_STATE
from main import MAX_STEPS as CLI_MAX_STEPS


def test_cli_and_web_use_the_same_default_puzzle():
    assert DEFAULT_CONFIG == get_default_config()
    assert (CLI_INITIAL_STATE, CLI_ATTACK_MAP, CLI_MAX_STEPS) == (
        INITIAL_STATE,
        ATTACK_MAP,
        MAX_STEPS,
    )


def test_default_config_does_not_share_mutable_attack_lists():
    first = get_default_config()
    first["attack_map"][1].append(99)

    assert 99 not in get_default_config()["attack_map"][1]
