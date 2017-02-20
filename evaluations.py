from state import *


def simple_eval(state, expanded_state):
    """
    Returns a heuristic estimate of the utility value of the given state,
    according to the rule that the utility should be positive when the board
    is in favour of  the king player, and negative when it is in favour of the
    dragon player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: to match function signature; ignored in this
        implementation
    :return: a heuristic estimate of the utility value of the given state
    :rtype: int
    """
    king_value = 1
    num_dragons = len(get_live_dragon_enumeration(state))
    num_guards = len(get_live_guards_enumeration(state))
    guard_weight = 5 / 4
    dragon_weight = 1
    dragon_score = num_dragons * dragon_weight
    guard_score = round(num_guards * guard_weight) + king_value
    return guard_score - dragon_score


def get_tiles_around(pos):
    """
    Get the numbers' of tiles around the board 
    position 'pos', orthogonally.
    
    :param pos: the board position of interest, 0-24
    :type pos: int
    :return: The number of tiles around the position 'pos'.
    :rtype: [int]
    """
    tiles = []
    left = pos - BOARD_NUM_RANKS
    right = pos + BOARD_NUM_RANKS
    above = pos + 1
    below = pos - 1
    size = BOARD_NUM_RANKS * BOARD_NUM_FILES
    if left < size and left >= 0:
        tiles.append(left)
    if right < size and right >= 0:
        tiles.append(right)
    if above % BOARD_NUM_RANKS != 0:
        tiles.append(above)
    if below % BOARD_NUM_RANKS != 0:
        tiles.append(below)
    return tiles


def is_king_at_risk(king_pos, expanded_state):
    """
    Return true or false depending on whether or not the king
    is in an orientation which is safe from check or not.
    
    :param king_pos: A number 0-24 indicating the placement of the
        king on the board:
    :type king_pos: int
    :param expanded_state: 
    :type expanded_state: dict(int, char)
    :return: True if there are three open spots around the king, 
        and false otherwise.
    :rtype: Boolean
    """
    surrounding_tiles = get_tiles_around(king_pos)

