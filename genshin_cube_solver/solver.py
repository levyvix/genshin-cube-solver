from .utils import get_logger
from concurrent.futures import ThreadPoolExecutor
from itertools import product


class CubeSolver:
    def __init__(self, initial_state: str, attack_map, max_steps: int) -> None:
        self.initial_state = list(map(int, initial_state.split()))
        self.attack_map = attack_map
        self.max_steps = max_steps
        self.logger = get_logger()
        self.STATE_VALUES = [1, 2, 3]

    def rotate_state(self, value: int) -> int:
        idx = self.STATE_VALUES.index(value)
        return self.STATE_VALUES[(idx + 1) % len(self.STATE_VALUES)]

    def apply_attack(
        self, state: list[int], attack_map: dict, attack: int
    ) -> list[int]:
        new_state = state.copy()
        for idx in attack_map[attack]:
            new_state[idx - 1] = self.rotate_state(new_state[idx - 1])
        return new_state

    def apply_sequence(self, state: list[int], attack_map: dict, sequence: tuple):
        for attack in sequence:
            state = self.apply_attack(state, attack_map, attack)
        return state

    def is_goal(self, state: list[int]):
        return all(val == state[0] for val in state)

    def try_sequence(self, task: tuple[list[int], dict, tuple]):
        state, attack_map, sequence = task

        result = self.apply_sequence(state.copy(), attack_map, sequence)

        if self.is_goal(result):
            return (sequence, result)

        return ((), [])

    def find_solution(self):
        """
        Encontra a menor sequência de ataques que leva todos os cubos a um estado igual.
        """
        self.logger.info(f"Buscando solução para estado inicial: {self.initial_state}")
        all_attacks = list(self.attack_map.keys())
        with ThreadPoolExecutor(10) as pool:
            for steps in range(1, self.max_steps + 1):
                self.logger.debug(f"Tentando sequências com {steps} passos...")
                sequences = product(all_attacks, repeat=steps)
                tasks = [
                    (self.initial_state, self.attack_map, seq) for seq in sequences
                ]
                for result in pool.map(self.try_sequence, tasks):
                    if result[0]:
                        self.logger.success(
                            f"Solução encontrada: ataques {result[0]} → estado final {result[1]}"
                        )
                        return result
        self.logger.warning("Nenhuma solução encontrada no limite de passos.")
        return (), []
