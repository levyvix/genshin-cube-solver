from itertools import product
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Tuple

from loguru import logger

# How many states the cube have
STATE_VALUES = [1, 2, 3]

INITIAL = [2, 1, 1, 3]  # In order, respecting the STATE_VALUES
ATTACK_MAP = {  # What happens when you attack one of the cubes, wich ones move with them?
    # Remember to include the self cube, if you attack 1 obviusly 1 will move
    1: [1, 2],
    2: [2, 3, 1],
    3: [3, 2, 4],
    4: [4, 3],
}


def rotate_state(value: int) -> int:
    """Gira o valor para o próximo estado cíclico."""
    idx = STATE_VALUES.index(value)
    return STATE_VALUES[(idx + 1) % len(STATE_VALUES)]


def apply_attack(
    state: List[int], attack_map: Dict[int, List[int]], attack: int
) -> List[int]:
    """Aplica um ataque e retorna novo estado."""
    new_state = state.copy()
    for idx in attack_map[attack]:
        new_state[idx - 1] = rotate_state(new_state[idx - 1])
    return new_state


def apply_sequence(
    state: List[int], attack_map: Dict[int, List[int]], sequence: Tuple[int, ...]
) -> List[int]:
    """Aplica uma sequência de ataques ao estado inicial."""
    for attack in sequence:
        state = apply_attack(state, attack_map, attack)
    return state


def is_goal(state: List[int]) -> bool:
    """
    Verifica se todos os cubos têm o mesmo valor.

    Args:
        state (List[int]): Estado atual dos cubos.

    Returns:
        bool: True se todos os cubos tiverem o mesmo valor, False caso contrário.

    Examples:
        >>> state = [1,1,1,1]
        >>> is_goal(state)
        True

    Essa função verifica se todos os cubos do estado atual têm o mesmo valor.
    Caso todos tenham o mesmo valor, retorna True, caso contrário retorna False.
    """
    return all(val == state[0] for val in state)


def try_sequence(
    args: Tuple[List[int], Dict[int, List[int]], Tuple[int, ...]],
) -> Tuple[Tuple[int, ...], List[int]]:
    """
    Attempts to apply a sequence of attacks to reach the goal state.

    Args:
        args (Tuple[List[int], Dict[int, List[int]], Tuple[int, ...]]):
            A tuple containing the current state, attack map, and the sequence of attacks.

    Returns:
        Tuple[Tuple[int, ...], List[int]]:
            Returns a tuple containing the sequence of attacks and the resulting state if the goal is reached;
            otherwise, returns an empty tuple and list.

    This function is used in multiprocessing to try different sequences of attacks
    on the state and check if the goal state is achieved.
    """
    state, attack_map, sequence = args
    # Apply the sequence of attacks to the copied state to prevent side-effects
    result = apply_sequence(state.copy(), attack_map, sequence)
    # Check if the resulting state is the goal state
    if is_goal(result):
        return (sequence, result)
    # Return an empty tuple and list if the goal is not reached
    return ((), [])


def find_solution(
    initial_state: List[int], attack_map: Dict[int, List[int]], max_steps: int = 6
) -> Tuple[Tuple[int, ...], List[int]]:
    """
    Encontra a menor sequência de ataques que leva todos os cubos a um estado igual.

    Args:
        initial_state (List[int]): Estado inicial dos cubos.
        attack_map (Dict[int, List[int]]): Mapa de ataques possíveis.
        max_steps (int): Número máximo de ataques para testar.

    Returns:
        Tuple[Tuple[int, ...], List[int]]: Sequência de ataques e estado final atingido.

    Examples:
        >>> initial = [2,2,3,2]
        >>> attack_map = {1:[1,2], 2:[3,1], 3:[2,4], 4:[1,3]}
        >>> find_solution(initial, attack_map)
        ([1, 2], [2, 2, 3, 2])

    """
    logger.info(f"Buscando solução para estado inicial: {initial_state}")
    all_attacks = list(attack_map.keys())
    with Pool(cpu_count()) as pool:
        for steps in range(1, max_steps + 1):
            logger.debug(f"Tentando sequências com {steps} passos...")
            sequences = product(all_attacks, repeat=steps)
            tasks = ((initial_state, attack_map, seq) for seq in sequences)
            for result in pool.imap_unordered(try_sequence, tasks, chunksize=1000):
                if result[0]:
                    logger.success(
                        f"Solução encontrada: ataques {result[0]} → estado final {result[1]}"
                    )
                    return result
    logger.warning("Nenhuma solução encontrada no limite de passos.")
    return (), []


if __name__ == "__main__":
    seq, final = find_solution(INITIAL, ATTACK_MAP, max_steps=10)
