from TranspositionTable import *
from state import *

_table = None
DEFAULT_DEPTH_LIMIT = 4

num_term = 0
num_leafs = 0
num_hits_and_other_stuff = 0
num_hits = 0
num_successors = 0
num_vs = 0


def init_table(max_size, replacement_policy):
    """
    Initializes the global transposition table with the given parameters.

    :param max_size:
    :param replacement_policy:
    :return:
    """
    global _table
    _table = TranspositionTable(max_size, replacement_policy)


def minimax(state, expanded_state, evaluate, age, remaining_depth):
    """
    Performs min search, returning a ((<utility>, <exact>), <move>) pair,
    where <utility> is the utility of <move>, <exact> is True iff <utility> is
    an exact value (as opposed to a heuristic estimate), and move is a move
    that will give a utility of <utility>. Note that <move> is None iff the
    given state is terminal, or remaining_depth starts off at 0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param age: an age counter, which increases (outside of calls to minimax)
        whenever a move is made that captures a piece
    :type age: int
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_hits_and_other_stuff
    global num_hits
    global num_successors
    global num_vs
    # We calculate the current depth of the search by subtracting the
    # remaining depth from the maximum depth.  Where the remaining depth is
    # 0, we will be 'max_depth' down the search tree.
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None:
        num_hits += 1
        if not value[DEPTH_INDEX] >= remaining_depth:
            print("value[DEPTH_INDEX] >= remaining_depth   => ",
                  value[DEPTH_INDEX], ">=", remaining_depth)
        elif not value[AGE_INDEX] >= age:
                print("value[AGE_INDEX] >= age   => ",
                      value[AGE_INDEX], ">=", age)
        else:
            num_hits_and_other_stuff += 1
            return ((value[SCORE_INDEX],
                    is_exact(value[EXACT_ALPHA_BETA_INDEX])),
                    value[MOVE_INDEX])
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        exact = True
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        exact = False
        best_move = None
    else:
        _successors = successors(state, expanded_state)
        num_successors += len(_successors)
        vs = [(minimax(new_state, new_expanded_state, evaluate, age,
                       remaining_depth - 1)[0], new_move) for
              new_state, new_expanded_state, new_move in
              _successors]
        num_vs += len(vs)
        if player_turn(state) == KING_PLAYER:
            (utility, exact), best_move = max(vs, key=lambda i: i[0][0])
        else:
            (utility, exact), best_move = min(vs, key=lambda i: i[0][0])
        _table[hash_string] = (remaining_depth, age, utility, best_move, exact)
    return (utility, exact), best_move


def alpha_beta_max(state, expanded_state, evaluate, age, remaining_depth,
                   alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs max search with alpha beta pruning, returning a
    ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to a
    heuristic estimate), and move is a move that will give a utility of
    <utility>. Note that <move> is None iff the given state is terminal, or
    remaining_depth starts off at 0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param age: an age counter, which increases (outside of calls to minimax)
        whenever a move is made that captures a piece
    :type age: int
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :param alpha:
    :type: alpha int
    :param beta:
    :type: beta int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_hits_and_other_stuff
    global num_hits
    global num_successors
    global num_vs
    # We calculate the current depth of the search by subtracting the
    # remaining depth from the maximum depth.  Where the remaining depth is
    # 0, we will be 'max_depth' down the search tree.
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None:
        num_hits += 1
        if not value[DEPTH_INDEX] >= remaining_depth:
            print("value[DEPTH_INDEX] >= remaining_depth   => ",
                  value[DEPTH_INDEX], ">=", remaining_depth)
        elif not value[AGE_INDEX] >= age:
            print("value[AGE_INDEX] >= age   => ",
                  value[AGE_INDEX], ">=", age)
        else:
            num_hits_and_other_stuff += 1
            return ((value[SCORE_INDEX],
                     is_exact(value[EXACT_ALPHA_BETA_INDEX])),
                    value[MOVE_INDEX])
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        exact = True
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        exact = False
        best_move = None
    else:
        _successors = successors(state, expanded_state)
        num_successors += len(_successors)
        utility = DRAGON_WIN
        best_move = None  # Not sure
        exact = None  # Not sure
        for successor in _successors:
            new_state, new_expanded_state, new_move = successor
            min_alpha_temp = alpha_beta_min(new_state, new_expanded_state,
                                            evaluate, age, remaining_depth - 1,
                                            alpha, beta)
            if utility < min_alpha_temp[0][0]:
                utility = min_alpha_temp[0][0]
                best_move = new_move
                exact = min_alpha_temp[0][1]

            if utility >= beta:
                return (utility, exact), best_move
            else:
                alpha = max(alpha, utility)
    return (utility, exact), best_move


def alpha_beta_min(state, expanded_state, evaluate, age, remaining_depth,
                   alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs minimax search with alpha beta pruning, returning a
    ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to a
    heuristic estimate), and move is a move that will give a utility of
    <utility>. Note that <move> is None iff the given state is terminal, or
    remaining_depth starts off at 0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param age: an age counter, which increases (outside of calls to minimax)
        whenever a move is made that captures a piece
    :type age: int
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :param alpha:
    :type: alpha int
    :param beta:
    :type: beta int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_hits_and_other_stuff
    global num_hits
    global num_successors
    global num_vs
    # We calculate the current depth of the search by subtracting the
    # remaining depth from the maximum depth.  Where the remaining depth is
    # 0, we will be 'max_depth' down the search tree.
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None:
        num_hits += 1
        if not value[DEPTH_INDEX] >= remaining_depth:
            print("value[DEPTH_INDEX] >= remaining_depth   => ",
                  value[DEPTH_INDEX], ">=", remaining_depth)
        elif not value[AGE_INDEX] >= age:
            print("value[_AGE_INDEX] >= age   => ",
                  value[AGE_INDEX], ">=", age)
        else:
            num_hits_and_other_stuff += 1
            return ((value[SCORE_INDEX],
                     is_exact(value[EXACT_ALPHA_BETA_INDEX])),
                    value[MOVE_INDEX])
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        exact = True
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        exact = False
        best_move = None
    else:
        _successors = successors(state, expanded_state)
        num_successors += len(_successors)
        utility = KING_WIN
        best_move = None  # Not sure
        exact = None  # Not sure
        for successor in _successors:
            new_state, new_expanded_state, new_move = successor
            max_alpha_temp = alpha_beta_max(new_state, new_expanded_state,
                                            evaluate, age, remaining_depth - 1,
                                            alpha, beta)
            if utility > max_alpha_temp[0][0]:
                utility = max_alpha_temp[0][0]
                best_move = new_move
                exact = max_alpha_temp[0][1]

            if utility <= alpha:
                return (utility, exact), best_move
            else:
                beta = min(beta, utility)
    return (utility, exact), best_move


def alpha_beta(state, expanded_state, evaluate, age, remaining_depth):
    """
    Performs minimax search with alpha beta pruning, returning a
    ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to a
    heuristic estimate), and move is a move that will give a utility of
    <utility>. Note that <move> is None iff the given state is terminal, or
    remaining_depth starts off at 0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param age: an age counter, which increases (outside of calls to minimax)
        whenever a move is made that captures a piece
    :type age: int
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """

    alpha = DRAGON_WIN
    beta = KING_WIN
    if player_turn(state) == KING_PLAYER:
        return alpha_beta_max(state, expanded_state, evaluate, age,
                              remaining_depth, alpha, beta)
    else:
        return alpha_beta_min(state, expanded_state, evaluate, age,
                              remaining_depth, alpha, beta)


if __name__ == "__main__":
    from evaluations import simple_eval
    import json
    import sys

    dummy_age = 0
    if len(sys.argv) > 1:
        depth_limit = int(sys.argv[1])
    else:
        depth_limit = DEFAULT_DEPTH_LIMIT
    print("Running minimax with a depth limit of", depth_limit)
    game_state = get_default_game_start()
    game_expanded_state = create_expanded_state_representation(game_state)
    u, m = minimax(game_state, game_expanded_state, simple_eval, dummy_age,
                   depth_limit)
    with open("minimax_depth_" + str(depth_limit) + ".json", 'w') as outfile:
        json.dump(_table.to_json_serializable(), outfile, indent=4)
    print("Final:", "util", u, "move", m, "terminal", num_term, "leafs",
          num_leafs, "hits", num_hits, "hits_+_more", num_hits_and_other_stuff,
          "successors", num_successors, "vs", num_vs)
