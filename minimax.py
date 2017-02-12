from State import *

table = dict() # mapping between states and (utility, move) pairs

def minimax(state, expanded_state):
    """
    Perform minimax search.
    :param state: the current node in the search
    :type state: array of bytes
    """
    global table

    if state in table:
        return table[state]
    is_term, who_won = is_terminal(state, expanded_state):
    if is_term:
        utility = who_won
        move = None
    else:
        vs = [(minimax(state, expanded_state)[0], move) for state, expanded_state, move in successors(state, expanded_state)]
        if player_turn(state) == KING_PLAYER:
            utility, move = arg_max(vs)
        elif player_turn(state) == DRAGON_PLAYER:
            utility, move = arg_min(vs)
    table[state] = (utility, move)
    return utility, move

def arg_max(vs):
    """
    Get the pair (utility, move) with the largest utility value.
    :param vs: A list of utility, move pairs.
    :type vs: [(int, (int, int))] (whatever a move is)
    :return: The (utility, move) tuple with the largest utility in the list.
    :rtype: (int, (int, int))
    """
    maxv, maxm = max(vs, key=lambda i:i[0])

def arg_min(vs):
    """
    Get the pair (utility, move) with the smallest utility value.
    :param vs: A list of utility, move pairs.
    :type vs: [(int, (int, int))] (whatever a move is)
    :return: The (utility, move) tuple with the smallest utility in the list.
    :rtype: (int, (int, int))
    """
    minv, minm = min(vs, key=lambda i:i[0])
