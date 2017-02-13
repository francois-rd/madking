from state import *

def simple_eval(state):
    dragons = len(get_live_dragon_enumeration(state))
    guards = len(get_live_guards_enumeration(state))
    if player_turn(state) is KING_PLAYER:
        return guards - dragons 
    else:
        return dragons - guards

    
