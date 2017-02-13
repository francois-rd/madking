from state import *


def simple_eval(state, expanded_state):
    """
    Returns <number-of-guards> - <number-of-dragons> if it's the king player's
    turn, and <number-of-dragons> - <number-of-guards> if it's the dragon
    player's turn.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: to match function signature; ignored in this
        implementation
    :return: <number-of-guards> - <number-of-dragons> if it's the king player's
        turn, and <number-of-dragons> - <number-of-guards> if it's the dragon
        player's turn
    :rtype: int
    """
    dragons = len(get_live_dragon_enumeration(state))
    guards = len(get_live_guards_enumeration(state))
    # TODO: so... the utility of the default initial state is negative for the
    #       king and positive for the dragon? This is wrong. The evaluation
    #       function should evaluate how good the board position is from player
    #       1's (the king's) point of view, regardless of who's turn it is.
    if player_turn(state) == KING_PLAYER:
        return guards - dragons
    else:
        return dragons - guards
