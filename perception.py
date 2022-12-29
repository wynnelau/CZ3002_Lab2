
import sys

from typing import Dict, List, Tuple
class Perception():
    CONFOUNDED = 0
    STENCH = 1
    TINGLE = 2
    GLITTER = 3
    BUMP = 4
    SCREAM = 5

    full_printout = ["Confounded", "Stench", "Tingle",
                     "Glitter", "Bump", "Scream"]

    short_printout = ['C', 'S', 'T', 'G', 'B', 'S']

    query_list: List[str]
    sense_printout: List[str]

    def __init__(self):
        self.query_list = ["off", "off", "off", "off", "off", "off"]
        self.sense_printout = ['C', 'S', 'T', 'G', 'B', 'S']

    def enable_perception(self, type: int):
        self.query_list[type] = "on"
        self.sense_printout[type] = self.full_printout[type]

    def disable_perception(self, type: int):
        self.query_list[type] = "off"
        self.sense_printout[type] = self.short_printout[type]

    def get_query_str(self) -> str:
        return ",".join(self.query_list)

    def get_sense_printout(self) -> str:
        return "-".join(self.sense_printout)