from state import *
import sys


def iterative_deepening_search(state, evaluate, search, age, max_depth):
    """
    Performs iterative-deepening search using the given search algorithm,
    returning the best result of the search algorithm.

    :param state: the root state of the search
    :type state: array of bytes
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a current depth, and a maximum depth, and
        returning a ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param age: an age counter, which increases (outside of calls to
        iterative_deepening_search) whenever a move is made that captures a
        piece
    :type age: int
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    player = player_turn(state)
    if player == KING_PLAYER:
        best_utility = -sys.maxsize
    else:
        best_utility = sys.maxsize
    best_exact = False
    best_move = None
    for depth in range(1, max_depth + 1):
        expanded_state = create_expanded_state_representation(state)
        (utility, exact), move = \
            search(state, expanded_state, evaluate, age, depth, depth)
        if player == KING_PLAYER:
            if utility > best_utility:
                best_utility = utility
                best_exact = exact
                best_move = move
        else:
            if utility < best_utility:
                best_utility = utility
                best_exact = exact
                best_move = move
    return (best_utility, best_exact), best_move


if __name__ == "__main__":
    from evaluations import simple_eval
    from minimax import minimax, DEFAULT_DEPTH_LIMIT

    dummy_age = 0
    game_state = get_default_game_start()
    print(iterative_deepening_search(game_state, simple_eval, minimax,
                                     dummy_age, DEFAULT_DEPTH_LIMIT))
