from state import *
import sys


def iterative_deepening_search(initial_state, evaluate, search, max_depth):
    """
    Performs iterative-deepening search using the given search algorithm,
    returning a (<utility>, <move>) pair. The move is None is the given state
    is terminal.

    :param initial_state: the root state of the search
    :type initial_state: array of bytes
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, a current depth, and a maximum depth, and
        returning a (<utility>, <move>) pair, where the move is None is the
        given state is terminal
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum depth to search
    :type max_depth: int
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    player = player_turn(initial_state)
    if player == KING_PLAYER:
        best_utility = -sys.maxsize
    else:
        best_utility = sys.maxsize
    best_move = None
    for depth in range(1, max_depth):
        expanded_state = create_expanded_state_representation(initial_state)
        utility, move = \
            search(initial_state, expanded_state, evaluate, depth, depth)
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
    from evaluations import simple_eval
    from minimax import minimax, DEFAULT_DEPTH_LIMIT

    state = get_default_game_start()
    print(iterative_deepening_search(state, simple_eval, minimax,
                                     DEFAULT_DEPTH_LIMIT))
