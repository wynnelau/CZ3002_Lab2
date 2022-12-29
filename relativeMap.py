import imp
#from map import *
from cell import *
import sys

from typing import Dict, List, Tuple
#from map import Map
import map
Map = map.Map

class RelativeMap(Map):
    center: List[int]

    def __init__(self, N, M, bumped):
        self.N = N
        self.M = M
        self.agent_angle_offset = 0
        self.center = [N//2, M//2]
        self.bumped = bumped

        self.create_map()

    def create_map(self):
        self.cells = []
        for y in range(self.M):
            row = []
            for x in range(self.N):
                cell = Cell()
                cell.coord = (x, y)
                row.append(cell)
            self.cells.append(row)