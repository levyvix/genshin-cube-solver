from genshin_cube_solver.solver import CubeSolver


INITIAL = "2 1 1 3"  # In order
ATTACK_MAP = {  # What happens when you attack one of the cubes, wich ones move with them?
    # Remember to include the self cube, if you attack 1 obviusly 1 will move
    1: [1, 2],
    2: [2, 3, 1],
    3: [3, 2, 4],
    4: [4, 3],
}
MAX_STEPS = 10


if __name__ == "__main__":
    solver = CubeSolver(INITIAL, ATTACK_MAP, max_steps=MAX_STEPS)
    seq, final = solver.find_solution()
