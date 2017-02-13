from state import *


def simple_eval(state):
    """
    Returns <number-of-guards> - <number-of-dragons> if it's the king player's
    turn, and <number-of-dragons> - <number-of-guards> if it's the dragon
    player's turn.

    :param state: the current node in the search
    :type state: array of bytes
    :return: <number-of-guards> - <number-of-dragons> if it's the king player's
        turn, and <number-of-dragons> - <number-of-guards> if it's the dragon
        player's turn
    :rtype: int
    """
    dragons = len(get_live_dragon_enumeration(state))
    guards = len(get_live_guards_enumeration(state))
    if player_turn(state) == KING_PLAYER:
        return guards - dragons
    else:
        return dragons - guards
