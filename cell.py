
import sys

from typing import Dict, List, Tuple
class Cell():
    coord: Tuple[int, int]
    grid: List[List[str]]

    def __init__(self):
        super().__init__()
        self.known_wall: bool = False
        self.elements: dict = {
            "wall": "off",
            "wumpus": "off",
            "confounded": "off",
            "portal": "off",
            "tingle": "off",
            "scream": "off",
            "glitter": "off",
            "stench": "off",
            "bump": "off",
        }
        self.make_empty()
        pass

    def make_empty(self, char=None):
        self.grid = [['.', '.', '.'], [' ', '?', ' '], ['.', '.', '.']]

    def reset_percepts(self):
        """Clears only parts of the cell that changes every update
        """
        self.grid[1] = [' ', '?', ' ']
        self.grid[2][0] = '.'
        self.grid[2][1] = '.'

    def wall_init(self):
        self.grid = [['#', '#', '#'], ['#', '#', '#'], ['#', '#', '#']]
        self.elements["wall"] = "on"

    def confounded_on(self):
        self.grid[0][0] = '%'

    def stench_on(self):
        self.grid[0][1] = '='

    def tingle_on(self):
        self.grid[0][2] = 'T'

    def npc_agent_on(self):
        self.grid[1][0] = '-'
        self.grid[1][2] = '-'

    def init_agent(self, dir: str):
        self.npc_agent_on()

        if dir == "rnorth":
            self.grid[1][1] = '∧'
        if dir == "reast":
            self.grid[1][1] = '>'
        if dir == "rsouth":
            self.grid[1][1] = 'V'
        if dir == "rwest":
            self.grid[1][1] = '<'

    def wumpus_on(self):
        self.npc_agent_on()
        self.grid[1][1] = 'W'

    def portal_on(self):
        self.npc_agent_on()
        self.grid[1][1] = 'O'

    def u_percept(self):
        self.npc_agent_on()
        self.grid[1][1] = 'U'

    def safe_on(self):
        self.grid[1][1] = 's'

    def visited_on(self):
        self.grid[1][1] = 'S'

    def glitter_on(self):
        self.grid[2][0] = '*'

    def bump_on(self):
        self.known_wall = True
        self.grid[2][1] = 'B'

    def bump_off(self):
        self.grid[2][1] = '.'

    def scream_on(self):
        self.grid[2][2] = '@'

    def pickup_gold(self):
        self.grid[2][0] = '.'
        self.elements["glitter"] = "off"

    def get_line(self, i: int):
        return self.grid[i]