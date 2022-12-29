:- dynamic([		
	move/2,
	visited/2,		% To indicate cell has been visited, asserted immediately when move(A,L) causes agent to move forward. Also asserted when agent arrives to the world.
	wumpus/2,		% Possible position of Wumpus to be inferred from smell. Reborn once agent is in same cell as alive wumpus.
	noWumpus/2,
	confundus/2,	% Possible position of Confundus to be inferred from tingle. Reposition once agent is in same cell as portal.
	noConfundus/2,
	tingle/2,		% Possible Confundus portals adjacent to cell with tingle.
	glitter/2,		% Coin present in cell
	stench/2,		% Possible Wumpus adjacent to cell with stench.
	safe/2,			% Cell will be safe only if it is visited and no confundus/wumpus.
	explore/1,
	current/3,		% Current position and direction of agent, updated everytime agent moves forward, turn right, or turn left.
	arrow/1,		% Only one arrow will be given to agent when reborn is called, arrow will be retracted once shot.
	wall/2,			% if world is 7x6, outer layer will be wall, hence actual playing area is 5x4.
	coin/2,
	existsWumpus/1,	% Activated only when arrow is shot, 0 when Wumpus is killed by arrow. Can be replaced by scream indicator turning on and staying on even after falling into confundus.
	confounded/2
	]).

% Cell contains Wumpus. Position resets to (0,0,rnorth), all memory lost, arrow returned to agent.
reborn:-
	% make sure to clear any previous facts stored
	resets,
	retractall(arrow(_)),
	assert(arrow(1)),
	retractall(coin(_,_)),
	retractall(existsWumpus(0)),
	assert(existsWumpus(1)).

% Cell contains Confundus portal. Position resets to (0,0,rnorth), 
% all memory lost except existence of uncollected coins, whether wumpus is alive and whether agent has arrow.
reposition([A,B,C,D,E,F]):-
	A == on,							% When we are on the condundus portal.
	current(X,Y,_),
	X \= 0,
	Y \= 0,
	resets.

resets:-
	retractall(visited(_,_)),
	retractall(wumpus(_,_)),
	retractall(confundus(_,_)),
	retractall(tingle(_,_)),
	retractall(glitter(_,_)),
	retractall(stench(_,_)),
	retractall(safe(_,_)),
	retractall(wall(_,_)),
	retractall(noWumpus(_,_)),
	retractall(noConfundus(_,_)),
	retractall(current(_,_,_)),
	assert(safe(0,0)),
	assert(current(0,0,rnorth)),		% The position of agent in relative map.
	assert(visited(0,0)).				


% A is Confounded, B is Stench, C is Tingle, D is Glitter, E is Bump, F is Scream

move(shoot,[A,B,C,D,E,F]):-
	shoot_arrow,
	setblock([A,B,C,D,E,F]).

shoot_arrow:-
	arrow(1),							% There has to be an arrow for the agent to shoot
	retract(arrow(1)).

move(moveforward,[A,B,C,D,E,F]):-
	move_forward,
	setblock([A,B,C,D,E,F]).
	
move(turnleft,[A,B,C,D,E,F]):-
	turn_left,
	setblock([A,B,C,D,E,F]).

move(turnright,[A,B,C,D,E,F]):-
	turn_right,
	setblock([A,B,C,D,E,F]).


move(pickup,[A,B,C,D,E,F]):-
	current(X,Y,_),
	glitter(X,Y),
	pick_up.

% A is Confounded, B is Stench, C is Tingle, D is Glitter, E is Bump, F is Scream
setblock([A,B,C,D,E,F]):-
	current(X,Y,Z),
	(((A == on, (((X\=0; Y\=0), resets);(X==0,Y==0)));(A == off)),
	((B == on, ((\+stench(X,Y),assert(stench(X,Y)));(stench(X,Y))));(B == off)),
	((C == on, ((\+tingle(X,Y),assert(tingle(X,Y)));(tingle(X,Y))));(C == off)),
	((D == on, ((coin(X,Y));((\+glitter(X,Y),assert(glitter(X,Y)))	;	(glitter(X,Y))	)));(D == off)),
	((E == on, bump_update);(E == off)),
	((F == on, scream_on);(F == off))),
	surveyadj(X,Y).
 


scream_on:-
	retractall(wumpus(_,_)),retract(existsWumpus(1)),assert(existsWumpus(0)),retractall(stench(_,_)).


%TODO: check 4 direction. Checks recursively for every action done.
explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First == moveforward,
	surveyadj(X,Y),
	((Z==reast,NewX is X+1,NewY is Y);(Z==rnorth,NewX is X,NewY is Y+1);(Z==rsouth,NewX is X,NewY is Y-1);(Z==rwest,NewX is X-1,NewY is Y)),
	safe(NewX,NewY), 			% ?? can we replace this with safe(NewX,NewY) instead, since safe(X,Y) is asserted in start searching
	move_forward,
	explore(Tail),
	retract(current(_,_,_)), 	% ?? why need this, should be asserted in move_forward
	assert(current(X,Y,Z)),		% ?? what is this for?
	assert(confounded(0,0)).

% Turn left if there is a wall.
explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First == moveforward,
	surveyadj(X,Y),
	((Z==reast,NewX is X+1,NewY is Y);(Z==rnorth,NewX is X,NewY is Y+1);(Z==rsouth,NewX is X,NewY is Y-1);(Z==rwest,NewX is X-1,NewY is Y)),
	(\+ safe(NewX,NewY); wall(NewX,NewY)),
	First=turnleft,
	turn_left,
	explore(Tail),
	retract(current(_,_,_)),
	assert(current(X,Y,Z)).

% Check turnleft
explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First==turnleft,
	turn_left,
	explore(Tail),
	retract(current(_,_,_)),
	assert(current(X,Y,Z)).

% Check turnright
explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First==turn_right,
	turn_right,
	explore(Tail),
	retract(current(_,_,_)),
	assert(current(X,Y,Z)).

% Check pickup
explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First==pickup,
	pick_up,
	explore(Tail),
	retract(current(_,_,_)),
	assert(current(X,Y,Z)).

explore([First|Tail]):-
	current(X,Y,Z),
	visited(X,Y),
	First==shoot,
	shoot_arrow,
	killWumpusIfPossible(X,Y,Z),
	explore(Tail).

% if agent is on a unvisited spot
explore(List_of_action):-
	current(X,Y,Z),
	(\+ visited(X,Y);\+safe(_,_)),		% shouldnt it be not visited and safe
	List_of_action=[].


explore(List_of_action):-
	current(X,Y,Z),
	\+safe(_,_),
	List_of_action==[].

hasarrow:-
	arrow(1).


surveyadj(X,Y):-
	stench(X,Y),
	tingle(X,Y),
	visited(X,Y),
	adjacent(X,Y, L),
	setWumpus(L),
	setConfundus(L).

% If the cell doesnt have tingle or stench, adjacent cells will be safe.
surveyadj(X,Y):-
	visited(X,Y),
	\+ stench(X,Y),
	\+ tingle(X,Y),
	(	(\+ safe(X,Y), assert(safe(X,Y)))	;	safe(X,Y)	),
	adjacent(X,Y,L),
	setsafeNoTingleNoStench(L).
setsafeNoTingleNoStench([A,B|Tail]):-
	(	(\+ safe(A,B), assert(safe(A,B)))	; 	safe(A,B)	),
	(	(confundus(A,B), retract(confundus(A,B)))	;	\+ confundus(A,B)	),
	(	(wumpus(A,B), retract(wumpus(A,B)))		;	\+ wumpus(A,B)	),
	(Tail == []	;	setsafeNoTingleNoStench(Tail)).

% If the adjacent cell has both noConfundus and noWumpus, itll be safe
surveyadj(X,Y):-
	visited(X,Y),
	adjacent(X,Y,L),
	setsafeNoConfundusNoWumpus(L).
setsafeNoConfundusNoWumpus([A,B|Tail]):-
	((wall(A,B));
	((visited(A,B);
	((noConfundus(A,B),
	noWumpus(A,B)),
	(	(\+ safe(A,B), assert(safe(A,B)))	; safe(A,B))))),
	(Tail == []	;	setsafeNoConfundusNoWumpus(Tail))).


% Check if the agent can perceive smell at this cell.
% If smelly, record that adjacent cells may have Wumpus.
surveyadj(X,Y):-
	stench(X,Y),
	visited(X,Y),
	adjacent(X,Y, L),
	setWumpus(L).
setWumpus([A,B|Tail]):-
	((visited(A,B);safe(A,B);noWumpus(A,B));
	(	(\+ wumpus(A,B), assert(wumpus(A,B)))	;	wumpus(A,B)	)),
	(Tail == []	;	setWumpus(Tail)).


% Check if the agent can perceive tingle at this cell.
% If tingle, record that adjacent cells may have confundus.
surveyadj(X,Y):-
	tingle(X,Y),
	visited(X,Y),
	adjacent(X,Y,L),
	setConfundus(L).
setConfundus([A,B|Tail]):-
	((visited(A,B);safe(A,B);noConfundus(A,B));
	(	(\+ confundus(A,B), assert(confundus(A,B)))	;	confundus(A,B)	)),
	(Tail == []	;	setConfundus(Tail)).

% If the cell doesnt have smell, retract possible Wumpus locations.
surveyadj(X,Y):-
	\+ stench(X,Y),
	visited(X,Y),
	adjacent(X,Y, L),
	setNoWumpus(L).
setNoWumpus([A,B|Tail]):-
	(	(wumpus(A,B), retract(wumpus(A,B)))		;	\+ wumpus(A,B)	),
	(	(\+ noWumpus(A,B), assert(noWumpus(A,B)))	;	noWumpus(A,B)	),
	(Tail == []	;	setNoWumpus(Tail)).


% If the cell doesnt have tingle, retract possible confundus locations.
surveyadj(X,Y):-
	\+ tingle(X,Y),
	visited(X,Y),
	adjacent(X,Y,L),
	setNoConfundus(L).
setNoConfundus([A,B|Tail]):-
	(	(confundus(A,B), retract(confundus(A,B)))	;	\+ confundus(A,B)	),
	(	(\+ noConfundus(A,B), assert(noConfundus(A,B)))	;	noConfundus(A,B)	),
	(Tail == []	;	setNoConfundus(Tail)).





% Generate adjacent positions of a given position.
adjacent(X, Y, L):-  
	XL is X-1,
    XR is X+1,
    YD is Y-1,
    YU is Y+1,
    append([XL, Y, XR, Y, X, YU, X, YD], [], L).







% Confirming there are no more than one possible recordings of Wumpus based on smell perceived,
% then killing Wumpus from a cell that aligns in a straight line with the Wumpus cell.
% To shoot towards pos y axis
killWumpusIfPossible(X,Y,Z):-
	wumpus(Xw, Yw), \+ moreThanOneWumpus, 	% ascertain Wumpus cell
	current(X,Y,Z),
	(X==Xw, Y<Yw, Z == rnorth),			% check Agent is in a cell thats in a straight line as Wumpus cell
	retractall(wumpus(_,_)),
	retractall(stench(_,_)),
	assert(existsWumpus(0)).

% To shoot towards pos x axis
killWumpusIfPossible(X,Y,Z):-
	wumpus(Xw, Yw), \+ moreThanOneWumpus, 	% ascertain Wumpus cell
	current(X,Y,Z),
	(Y==Yw, X<Xw, Z == reast),			% check Agent is in a cell thats in a straight line as Wumpus cell
	retractall(wumpus(_,_)),
	retractall(stench(_,_)),
	assert(existsWumpus(0)).

% To shoot towards neg y axis
killWumpusIfPossible(X,Y,Z):-
	wumpus(Xw, Yw), \+ moreThanOneWumpus, 	% ascertain Wumpus cell
	current(X,Y,Z),
	(X==Xw, Y>Yw, Z == rsouth),			% check Agent is in a cell thats in a straight line as Wumpus cell
	retractall(wumpus(_,_)),
	retractall(stench(_,_)),
	assert(existsWumpus(0)).

% To shoot towards neg x axis
killWumpusIfPossible(X,Y,Z):-
	wumpus(Xw, Yw), \+ moreThanOneWumpus, 	% ascertain Wumpus cell
	current(X,Y,Z),
	(Y==Yw, X>Xw, Z == rwest),			% check Agent is in a cell thats in a straight line as Wumpus cell
	retractall(wumpus(_,_)),
	retractall(stench(_,_)),
	assert(existsWumpus(0)).

moreThanOneWumpus:-
  wumpus(X,Y), wumpus(A,B), X\=A,Y\=B.



bump_update:-
	current(X,Y,Z),
	Z == rnorth,
	NewY is Y-1,
	(wall(X,Y);(\+wall(X,Y),assert(wall(X,Y)))),
	assert(current(X,NewY,Z)),
	retract(current(X,Y,Z)),
	((safe(X,Y),retract(safe(X,Y)));\+safe(X,Y)).

bump_update:-
	current(X,Y,Z),
	Z == reast,
	NewX is X-1,
	(wall(X,Y);(\+wall(X,Y),assert(wall(X,Y)))),
	assert(current(NewX,Y,Z)),
	retract(current(X,Y,Z)),
	((safe(X,Y),retract(safe(X,Y)));\+safe(X,Y)).

bump_update:-
	current(X,Y,Z),
	Z == rsouth,
	NewY is Y+1,
	(wall(X,Y);(\+wall(X,Y),assert(wall(X,Y)))),
	assert(current(X,NewY,Z)),
	retract(current(X,Y,Z)),
	((safe(X,Y),retract(safe(X,Y)));\+safe(X,Y)).

bump_update:-
	current(X,Y,Z),
	Z == rwest,
	NewX is X+1,
	(wall(X,Y);(\+wall(X,Y),assert(wall(X,Y)))),
	assert(current(NewX,Y,Z)),
	retract(current(X,Y,Z)),
	((safe(X,Y),retract(safe(X,Y)));\+safe(X,Y)).


move_forward:-
	current(X,Y,Z),
	Z == rnorth,
	NewY is Y+1,
	assert(current(X,NewY,Z)),
	(visited(X,NewY);assert(visited(X,NewY))),
	retract(current(X,Y,Z)).

move_forward:-
	current(X,Y,Z),
	Z == reast,
	NewX is X+1,
	assert(current(NewX,Y,Z)),
	(visited(NewX,Y);assert(visited(NewX,Y))),
	retract(current(X,Y,Z)).

move_forward:-
	current(X,Y,Z),
	Z == rsouth,
	NewY is Y-1,
	assert(current(X,NewY,Z)),
	(visited(X,NewY);assert(visited(X,NewY))),
	retract(current(X,Y,Z)).

move_forward:-
	current(X,Y,Z),
	Z == rwest,
	NewX is X-1,
	assert(current(NewX,Y,Z)),
	(visited(NewX,Y);assert(visited(NewX,Y))),
	retract(current(X,Y,Z)).

turn_left:-
	current(X,Y,Z),
	((Z == rnorth,
	assert(current(X,Y,rwest)),
	retract(current(X,Y,rnorth)));
	(Z == rwest,
	assert(current(X,Y,rsouth)),
	retract(current(X,Y,rwest)));
	(Z == rsouth,
	assert(current(X,Y,reast)),
	retract(current(X,Y,rsouth)));
	(Z == reast,
	assert(current(X,Y,rnorth)),
	retract(current(X,Y,reast)))).


turn_right:-
	current(X,Y,Z),
	((Z == rnorth,
	assert(current(X,Y,reast)),
	retract(current(X,Y,rnorth)));
	(Z == rwest,
	assert(current(X,Y,rnorth)),
	retract(current(X,Y,rwest)));
	(Z == rsouth,
	assert(current(X,Y,rwest)),
	retract(current(X,Y,rsouth)));
	(Z == reast,
	assert(current(X,Y,rsouth)),
	retract(current(X,Y,reast)))).


pick_up:-
	current(X,Y,_),
	glitter(X,Y),
	assert(coin(X,Y)),
	retract(glitter(X,Y)).

