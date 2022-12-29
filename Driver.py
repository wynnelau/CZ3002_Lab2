
import sys

from typing import Dict, List, Tuple
from pyswip import *
from relativeMap import *
from knowledge import *
from perception import *
from cell import *
from map import *

def setup_map(N: int, M: int) -> Map:
    a_map = Map(N, M, "rnorth")
    a_map.reposition_agent(3, 3)

    a_map.add_wumpus(5, 4)

    a_map.add_coin(2, 3)
    a_map.add_coin(3, 2)

    a_map.add_portal(2, 1)
    a_map.add_portal(4, 1)
    a_map.add_portal(4, 4)

    return a_map


def setup_prolog(filename: str, a_map: Map) -> Prolog:
    # initialise prolog file
    prolog = Prolog()
    prolog.consult(filename)
    list(prolog.query("reborn"))

    # send initial perceptions to agent
    perceptions = a_map.get_cell_perceptions()
    list(prolog.query(f"reposition([{perceptions.get_query_str()}])"))

    return prolog


def make_action(prolog: Prolog, a_map: Map, action: str = None,
                print_map: bool = True, print_rel: bool = False, print_abs: bool = False):
    # preemptively clears bumps to prevent old bumps from showing
    a_map.clear_transient_indicators()

    # updates map with action
    a_map.do_action(action)

    # get new perceptions from cell after action
    perceptions = a_map.get_cell_perceptions()

    # update agent with new perceptions
    query_str = f"move({action}, [{perceptions.get_query_str()}])"
    print(query_str)
    list(prolog.query(query_str))

    # reposition if stepped on a confundus portal
    if a_map.check_portal():
        print("Agent stepped on a portal")
        a_map.reposition_agent(1, 4)
        perceptions = a_map.get_cell_perceptions()
        list(prolog.query(f"reposition([{perceptions.get_query_str()}])"))

    # print out map and relevant info
    if print_map:
        print(f"[Driver] {perceptions.get_sense_printout()}")
        if print_abs:
            a_map.print_absolute_map(prolog)
        if print_rel:
            a_map.print_relative_map(prolog)


def auto_explore(prolog: Prolog, a_map: Map):
    path_exists = True

    while path_exists:
        L = list(prolog.query("explore(L)"))
        path_exists = handle_explore_result(prolog, a_map, L)

    print("[Driver] Nothing from explore/1 anymore...")
    t = list(prolog.query("safe(X,Y), \+visited(X,Y)"))
    return


def handle_explore_result(prolog: Prolog, a_map: Map, L: List[Dict[str, List[Atom]]]) -> bool:
    if len(L) == 0:
        return False

    actions = L[0]['L']
    for action in actions[:-1]:
        make_action(prolog, a_map, action)
    make_action(prolog, a_map, actions[-1], True, True)

    return True


def printout_glitter_visited_safe():
    a_map = setup_map(7, 6)
    prolog = setup_prolog("agent.pl", a_map)

    print("===[Complete Absolute Map]===")
    a_map.print_init_map()

    print("===[Testing glitter/2, safe/2, visited/2 and pickup]===")
    print("Moving agent to (0, 1) first")
    make_action(prolog, a_map, "moveforward", True, True)
    print("Agent now picks up the coin")
    make_action(prolog, a_map, "pickup", True, True)
    print("The glitter indicator on (0, 1) should now be gone")
    print("Now moving agent to (-1, 0), only printing relative map for last action")
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "moveforward", True, True)
    print("Agent now picks up the second coin")
    make_action(prolog, a_map, "pickup", True, True)
    print("The glitter indicator on (-1, 0) should now be gone")

    safe = list(prolog.query("safe(X, Y)"))
    visited = list(prolog.query("visited(X, Y)"))

    safe = [f"({cell['X']}, {cell['Y']})" for cell in safe]
    visited = [f"({cell['X']}, {cell['Y']})" for cell in visited]

    print("safe/2 and visited/2 outputs should match the relative map")
    print(f"Safe cells: {', '.join(safe)}")
    print(f"Visited cells: {', '.join(visited)}")
    print("\n")


def printout_confundus_tingle():
    a_map = setup_map(7, 6)
    prolog = setup_prolog("agent.pl", a_map)

    print("===[Complete Absolute Map]===")
    a_map.print_init_map()

    print("===[Testing confundus/2 and tingle/2]===")
    print("Moving agent to (-1, 1) first")
    make_action(prolog, a_map, "turnleft", False, False)
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "moveforward", True, True)
    print("Tingle indicator should show and portals should surround the player")
    print("But cells that are safe or visited should not be portals")
    print("Now moving agent to (0, -2)")
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "turnleft", False, False)
    make_action(prolog, a_map, "moveforward", True, True)

    confundus = list(prolog.query("confundus(X, Y)"))
    tingle = list(prolog.query("tingle(X, Y)"))

    confundus = [f"({cell['X']}, {cell['Y']})" for cell in confundus]
    tingle = [f"({cell['X']}, {cell['Y']})" for cell in tingle]

    print("confundus/2 and tingle/2 outputs should match the relative map")
    print(f"Confundus cells: {', '.join(confundus)}")
    print(f"Tingle cells: {', '.join(tingle)}")
    print("\n")


def printout_wumpus_stench_bump_current():
    a_map = setup_map(7, 6)
    prolog = setup_prolog("agent.pl", a_map)

    print("===[Complete Absolute Map]===")
    a_map.print_init_map()

    print("===[Testing wumpus/2, stench/2, wall/2, bump, scream and shoot]===")
    print("Now moving agent to (2, 0)")
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "moveforward", True, True)
    print("Stench indicator should show and wumpus should surround the player")
    print("But cells that are safe or visited should not be wumpuses (wumpi?)")
    print("Now we move the agent to (3, 0) which is a wall")
    make_action(prolog, a_map, "moveforward", True, True)
    print("The bump indicator should show and (3, 0) should update to be a wall")

    wumpus = list(prolog.query("wumpus(X, Y)"))
    stench = list(prolog.query("stench(X, Y)"))
    wall = list(prolog.query("wall(X, Y)"))

    wumpus = [f"({cell['X']}, {cell['Y']})" for cell in wumpus]
    stench = [f"({cell['X']}, {cell['Y']})" for cell in stench]
    wall = [f"({cell['X']}, {cell['Y']})" for cell in wall]

    print("wumpus/2, stench/2 and wall/2 outputs should match the relative map")
    print(f"Wumpus cells: {', '.join(wumpus)}")
    print(f"Stench cells: {', '.join(stench)}")
    print(f"Wall cells: {', '.join(wall)}")

    print("We now want to check if our agent has the arrow")
    arrow = list(prolog.query("hasarrow"))
    print("Agent has arrow: ", len(arrow) > 0)

    print("Since we know the wumpus' location beforehand, let's shoot it")
    make_action(prolog, a_map, "turnright", False, False)
    make_action(prolog, a_map, "shoot", True, True)
    print("The wumpus should now be dead and all wumpus cells should be removed")
    print("And we check again if the agent has the arrow")
    arrow = list(prolog.query("hasarrow"))
    print("Agent has arrow: ", len(arrow) > 0)

    print("Finally we check the agent's current relative position")
    current = list(prolog.query("current(X, Y, Dir)"))[0]
    print(f"Current: [{current['X']}, {current['Y']}, {current['Dir']}]")
    print("It should be [2, 0, rsouth]")
    print("\n")


def printout_reposition():
    a_map = setup_map(7, 6)
    prolog = setup_prolog("agent.pl", a_map)

    print("===[Complete Absolute Map]===")
    a_map.print_init_map()

    print("===[Testing reposition/1]===")
    print("Moving agent to (0, 2) first")
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "turnright", True, True)
    print("If we take a portal from any direction, the absolute direction should stay the same")
    print("But the relative direction should reset to north")
    print("In this case, we teleport the agent to (1, 4) on the absolute map")
    make_action(prolog, a_map, "moveforward", True, True, True)

    print("Any movement we make should update accordingly")
    print("Let's move the agent to relative (-1, 1)")
    make_action(prolog, a_map, "moveforward", False, False)
    make_action(prolog, a_map, "turnleft", False, False)
    make_action(prolog, a_map, "moveforward", True, True, True)
    print("On the absolute map, the agent should move east then north")
    print("But on the relative map, north then west")

    print("\n")


def printout_explore():
    a_map = setup_map(7, 6)
    prolog = setup_prolog("agent.pl", a_map)

    print("===[Complete Absolute Map]===")
    a_map.print_init_map()

    print("===[Testing explore/1]===")
    print("Driver will just keep repeatedly calling explore/1 and running all actions provided")
    print("Relative map will only be printed for the last action for each explore/1 call to make it easier to follow")
    print("action/2 queries will still be printed for each action")
    print("See you at the end of the printout :)")
    print("\n")

    auto_explore(prolog, a_map)
    make_action(prolog, a_map, "none", True, True, True)
    print("Agent should now be at relative (0, 0) and all possible safe cells are visited")
    print("All available coins should also have been picked up")
    print("All the 'border' cells should either be wumpus, confundus portals or walls")

    print("\n")


def printout_loc_map_sensory():
    printout_glitter_visited_safe()
    printout_confundus_tingle()
    printout_wumpus_stench_bump_current()
    printout_reposition()
    printout_explore()


def main():
    #filename = "testPrintout-Self-Self.txt"
    #sys.stdout = open(file=filename, mode="w+", encoding="utf8")
    #printout_loc_map_sensory()
    a_map = setup_map(7, 6)
    a_map.print_init_map()


if __name__ == "__main__":
    main()
