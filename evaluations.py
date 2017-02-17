from state import *


def simple_eval(state, expanded_state):
    """
    Get the utility value of the state according to the rule
    '' '' 
    This value should be positive when the board is in favour of 
    the King's team, and negative when it is in favour of the Dragon's
    team.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: to match function signature; ignored in this
        implementation
    :return: 
    :rtype: int
    """
    king_value = 1
    num_dragons = len(get_live_dragon_enumeration(state))
    num_guards = len(get_live_guards_enumeration(state))
    guard_weight = (5/4)
    dragon_weight = 1
    dragon_score = num_dragons * dragon_weight
    guard_score = round(num_guards * guard_weight) + king_value
    return guard_score - dragon_score

