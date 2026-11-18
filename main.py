from genshin_cube_solver.solver import CubeSolver
from genshin_cube_solver.defaults import ATTACK_MAP, INITIAL_STATE, MAX_STEPS


if __name__ == "__main__":
    solver = CubeSolver(INITIAL_STATE, ATTACK_MAP, max_steps=MAX_STEPS)
    seq, final = solver.find_solution()
