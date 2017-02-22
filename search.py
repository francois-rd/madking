from state import *
import sys


def iterative_deepening_search(state, expanded_state, evaluate, search,
                               max_depth):
    """
    Performs iterative-deepening search using the given search algorithm,
    returning the best result of the search algorithm.

    :param state: the root state of the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    player = player_turn(state)
    if player == KING_PLAYER:
        best_utility = -sys.maxsize
    else:
        best_utility = sys.maxsize
    best_move = None
    for depth in range(1, max_depth + 1):
        utility, move = search(state, expanded_state, evaluate, depth)
        if player == KING_PLAYER:
            if utility > best_utility:
                best_utility = utility
                best_move = move
        else:
            if utility < best_utility:
                best_utility = utility
                best_move = move
    return best_utility, best_move


if __name__ == "__main__":
    from Main import defaults
    from evaluations import simple_eval
    from minimax import init_table, minimax, DEFAULT_DEPTH_LIMIT

    init_table(defaults['table-size'],
               defaults['replace'][defaults['replace_name']])
    game_state = get_default_game_start()
    _expanded_state = create_expanded_state_representation(game_state)
    print(iterative_deepening_search(game_state, _expanded_state, simple_eval,
                                     minimax, DEFAULT_DEPTH_LIMIT))
