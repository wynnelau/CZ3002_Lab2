
import sys

from typing import Dict, List, Tuple
from cell import *
from perception import *
from knowledge import *
#from relativeMap import *
from pyswip import *
#from relativeMap import RelativeMap
import relativeMap
class Map():
    N: int
    M: int
    rel_map_size: List[int] = [3, 3]
    agent_start: List[int]
    agent_pos: List[int]
    agent_abs_dir: str
    agent_angle_offset: int = 0
    bumped: bool
    scream: bool

    cells: List[List[Cell]]
    wumpus_pos = List[int]

    def __init__(self, N: int, M: int, dir: str) -> None:
        super().__init__()
        self.N = N
        self.M = M
        self.agent_abs_dir = dir
        self.bumped = False
        self.scream = False

        self.init_map()

    def init_map(self):
        self.create_map()
        self.draw_walls()

    def create_map(self):
        self.cells = []

        for y in range(self.M):
            row = []
            for x in range(self.N):
                cell = Cell()
                cell.coord = (x, y)
                row.append(cell)
            self.cells.append(row)

    def draw_walls(self):
        for row in range(self.M):
            for col in range(self.N):
                if row == 0 or row == (self.M-1):
                    self.cells[row][col].wall_init()
                if col == 0 or col == (self.N-1):
                    self.cells[row][col].wall_init()

    def reset_map(self):
        for row in range(self.M):
            for col in range(self.N):
                cell = self.cells[row][col]
                if cell.elements["wall"] != "on":
                    cell.elements["confounded"] = "off"
                    cell.make_empty()

    def reposition_agent(self, X: int, Y: int):
        self.reset_map()
        self.rel_map_size = [3, 3]
        self.agent_start = [X, Y]
        self.agent_pos = [X, Y]
        self.cells[Y][X].elements["confounded"] = "on"

        # angle offset is based on clockwise direction
        # so if currently facing east and enter a portal,
        # offset of relative to absolute direction is 90 degrees after repositioning
        dirs = ["rnorth", "reast", "rsouth", "rwest"]
        self.agent_angle_offset += dirs.index(self.agent_abs_dir) * 90
        self.agent_angle_offset %= 360

    def add_coin(self, X: int, Y: int):
        cell = self.cells[Y][X]
        cell.elements["glitter"] = "on"

    def add_wall(self, X: int, Y: int):
        cell = self.cells[Y][X]
        cell.wall_init()

    def add_wumpus(self, X: int, Y: int):
        self.wumpus_pos = [X, Y]
        cell = self.cells[Y][X]
        cell.elements["wumpus"] = "on"
        self.set_adjacent_element(X, Y, "stench")

    def add_portal(self, X: int, Y: int):
        cell = self.cells[Y][X]
        cell.elements["portal"] = "on"
        self.set_adjacent_element(X, Y, "tingle")

    def clear_transient_indicators(self):
        self.bumped = False
        self.scream = False

    def set_adjacent_element(self, X: int, Y: int, element):
        self.cells[Y-1][X].elements[element] = "on"
        self.cells[Y][X-1].elements[element] = "on"
        self.cells[Y][X+1].elements[element] = "on"
        self.cells[Y+1][X].elements[element] = "on"

    def do_action(self, action: str):
        """Updates map according to action generated
        Args:
            action (str): Action the agent will take
        """

        if action == "pickup":
            cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
            cell.pickup_gold()

        elif action == "shoot":
            ax, ay = self.agent_pos
            adir = self.agent_abs_dir
            wx, wy = self.wumpus_pos

            self.scream = (
                ay == wy and ax > wx and adir == "rwest" or
                ay == wy and ax < wx and adir == "reast" or
                ay > wy and ax == wx and adir == "rnorth" or
                ay < wy and ax == wx and adir == "rsouth"
            )

        elif action == "moveforward":
            prev_pos = self.agent_pos.copy()

            if self.agent_abs_dir == "rnorth":
                self.agent_pos[1] -= 1
            elif self.agent_abs_dir == "reast":
                self.agent_pos[0] += 1
            elif self.agent_abs_dir == "rsouth":
                self.agent_pos[1] += 1
            elif self.agent_abs_dir == "rwest":
                self.agent_pos[0] -= 1

            # checks for wall collision
            cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
            if cell.elements["wall"] == "on":
                self.agent_pos = prev_pos
                self.bumped = True
                cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
                cell.bump_on()

            # check if relative map needs resizing
            dx = abs(abs(self.agent_pos[0]) - self.agent_start[0])
            dy = abs(abs(self.agent_pos[1]) - self.agent_start[1])

            # because expansion of relative map depends on relative x/y width explored
            if self.agent_angle_offset % 180 == 0:
                self.rel_map_size[0] = max(dx*2 + 3, self.rel_map_size[0])
                self.rel_map_size[1] = max(dy*2 + 3, self.rel_map_size[1])
            else:
                self.rel_map_size[1] = max(dx*2 + 3, self.rel_map_size[1])
                self.rel_map_size[0] = max(dy*2 + 3, self.rel_map_size[0])

        elif action == "turnleft":
            if self.agent_abs_dir == "rnorth":
                self.agent_abs_dir = "rwest"
            elif self.agent_abs_dir == "reast":
                self.agent_abs_dir = "rnorth"
            elif self.agent_abs_dir == "rsouth":
                self.agent_abs_dir = "reast"
            elif self.agent_abs_dir == "rwest":
                self.agent_abs_dir = "rsouth"

        elif action == "turnright":
            if self.agent_abs_dir == "rnorth":
                self.agent_abs_dir = "reast"
            elif self.agent_abs_dir == "reast":
                self.agent_abs_dir = "rsouth"
            elif self.agent_abs_dir == "rsouth":
                self.agent_abs_dir = "rwest"
            elif self.agent_abs_dir == "rwest":
                self.agent_abs_dir = "rnorth"

    def check_portal(self) -> bool:
        cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
        return cell.elements["portal"] == "on"

    def get_cell_perceptions(self):
        """Retrives current perceptions L of the agent
        """

        cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
        perception = Perception()

        if cell.elements["confounded"] == "on":
            perception.enable_perception(Perception.CONFOUNDED)
        if cell.elements["stench"] == "on":
            perception.enable_perception(Perception.STENCH)
        if cell.elements["tingle"] == "on":
            perception.enable_perception(Perception.TINGLE)
        if cell.elements["glitter"] == "on":
            perception.enable_perception(Perception.GLITTER)
        if self.bumped:
            perception.enable_perception(Perception.BUMP)
        if self.scream:
            perception.enable_perception(Perception.SCREAM)

        return perception

    def update_map_with_perceptions(self, prolog: Prolog, ref: List[int], abs_dir: bool):
        """Adds to the map the current perceptions of the agent
        Args:
            prolog (Prolog): The initialised prolog file of agent
            ref (List[int]): Reference coordinate that the X and Y offsets are based off of
                             Eg (ref = [3, 3] means that a relative coordinate of (1, 3) is (4, 6) 
                             if initial relative and absolute direction are the same)
        """

        knawledge = Knawledge(prolog)

        for kb in knawledge.kb:
            for data in kb["data"]:
                # relative X and Y positions may not correspond with absolute X and Y positions
                # so adjust accordingly

                # both directions are the same
                if self.agent_angle_offset == 0:
                    X = ref[0] + data['X']
                    Y = ref[1] - data['Y']

                # eg. relative = rnorth, absolute = rsouth
                elif self.agent_angle_offset == 180:
                    X = ref[0] - data['X']
                    Y = ref[1] + data['Y']

                # eg. relative = rnorth, absolute = reast
                elif self.agent_angle_offset == 90:
                    X = ref[0] + data['Y']
                    Y = ref[1] + data['X']

                # eg. relative = rnorth, absolute = rwest
                elif self.agent_angle_offset == 270:
                    X = ref[0] - data['Y']
                    Y = ref[1] - data['X']

                cell = self.cells[Y][X]

                # no need to update walls
                if cell.elements["wall"] == "on":
                    continue

                if kb["type"] == Knawledge.VISITED:
                    cell.visited_on()
                elif kb["type"] == Knawledge.SAFE:
                    cell.safe_on()
                elif kb["type"] == Knawledge.WUMPUS:
                    cell.wumpus_on()
                elif kb["type"] == Knawledge.STENCH:
                    cell.stench_on()
                elif kb["type"] == Knawledge.CONFOUNDED:
                    cell.confounded_on()
                elif kb["type"] == Knawledge.CONFUNDUS:
                    cell.portal_on()
                elif kb["type"] == Knawledge.TINGLE:
                    cell.tingle_on()
                elif kb["type"] == Knawledge.GLITTER:
                    cell.glitter_on()
                elif kb["type"] == Knawledge.U:
                    cell.u_percept()
                elif kb["type"] == Knawledge.WALL:
                    cell.wall_init()
                elif kb["type"] == Knawledge.AGENT:
                    if abs_dir:
                        cell.init_agent(self.agent_abs_dir)
                    else:
                        cell.init_agent(data["Dir"])
                    if self.bumped:
                        cell.bump_on()

    def reset_absolute_map(self, full_clear: bool = False):
        """Clears all of the cell drawing back to an empty map
        """
        for row in self.cells:
            for cell in row:
                if cell.elements["wall"] == "on":
                    cell.wall_init()
                else:
                    if full_clear:
                        cell.make_empty()
                    else:
                        cell.clear_dynamic_perceptions()

    def generate_relative_map(self, prolog: Prolog):
        """Creates a relative map based on agent perceptions
        Args:
            prolog (Prolog): The initialised prolog file of agentv
        Returns:
            RelativeMap: The relative map with drawn cells
        """

        r_map = relativeMap.RelativeMap(*self.rel_map_size, self.bumped)
        r_map.update_map_with_perceptions(prolog, r_map.center, False)
        return r_map

    def print_relative_map(self, prolog: Prolog):
        r_map = self.generate_relative_map(prolog)
        r_map.print_map()

    def print_absolute_map(self, prolog: Prolog):
        self.reset_absolute_map(full_clear=False)
        self.update_map_with_perceptions(prolog, self.agent_start, True)
        self.print_map()

    def update_map_with_data(self):
        """Draws map with absolute data
        """
        for row in self.cells:
            for cell in row:
                # don't update if it's a wall
                if cell.elements["wall"] == "on":
                    continue

                if cell.elements["wumpus"] == "on":
                    cell.wumpus_on()
                if cell.elements["stench"] == "on":
                    cell.stench_on()
                if cell.elements["portal"] == "on":
                    cell.portal_on()
                if cell.elements["tingle"] == "on":
                    cell.tingle_on()
                if cell.elements["glitter"] == "on":
                    cell.glitter_on()

    def draw_agent(self):
        cell = self.cells[self.agent_pos[1]][self.agent_pos[0]]
        cell.init_agent(self.agent_abs_dir)

    def print_init_map(self):
        """Prints initial absolute map
        """
        self.reset_absolute_map(full_clear=True)
        self.update_map_with_data()
        self.draw_agent()
        self.print_map()

    def print_map(self):
        print('-' * (6*self.N+1))
        for row in self.cells:
            line_0 = [cell.get_line(0) for cell in row]
            line_1 = [cell.get_line(1) for cell in row]
            line_2 = [cell.get_line(2) for cell in row]

            print('|', end='')
            for cell in line_0:
                print(" ".join(cell), end='|')
            print("\n|", end='')
            for cell in line_1:
                print(" ".join(cell), end='|')
            print("\n|", end='')
            for cell in line_2:
                print(" ".join(cell), end='|')
            print('')
            print('-' * (6*self.N+1))
