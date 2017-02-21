from TranspositionTable import *
from state import *

_table = None
DEFAULT_DEPTH_LIMIT = 4

num_term = 0
num_leafs = 0
num_usable_hits = 0


def init_table(max_size, replacement_policy):
    """
    Initializes the global transposition table with the given parameters.

    :param max_size: the maximum number of entries in the table
    :type max_size: integral
    :param replacement_policy: a function that takes a TranspositionTable, a
        key, and a value, and returns a key and a value, which is either one of
        the entries in the table whose value is the best candidate for removal
        when the table is full and a new entry must be added, or is the key and
        value of the given/new entry, which is itself not good enough to be
        added to the table (i.e. the new entry is rejected)
    :type replacement_policy: (TranspositionTable, X, Y) => X, Y, where X is
        the type of the keys in this table, and Y is the type of the values
    """
    global _table
    _table = TranspositionTable(max_size, replacement_policy)


def dump_table(filename):
    """
    Prints the global transposition table to the file with the given name in
    JSON format.

    :param filename: the name of the file to which to prints the table
    """
    import json

    global _table
    with open(filename, 'w') as outfile:
        json.dump(_table.to_json_serializable(), outfile, indent=1)


def minimax(state, expanded_state, evaluate, remaining_depth):
    """
    Performs minimax search, returning a ((<utility>, <exact>), <move>) pair,
    where <utility> is the utility of <move>, <exact> is unconditionally True,
    and move is a move that will give a utility of <utility>. Note that <move>
    is None iff the given state is terminal, or 'remaining_depth' starts off at
    0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
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
    global num_usable_hits
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        return (value[SCORE_INDEX],
                is_exact(value[FLAGS_INDEX])), value[MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        best_move = None
    else:
        vs = [(minimax(new_state, new_expanded_state, evaluate,
                       remaining_depth - 1)[0], new_move) for
              new_state, new_expanded_state, new_move in
              successors(state, expanded_state)]
        if player_turn(state) == KING_PLAYER:
            (utility, exact), best_move = max(vs, key=lambda i: i[0][0])
        else:
            (utility, exact), best_move = min(vs, key=lambda i: i[0][0])
        _table[hash_string] = (remaining_depth, utility, best_move,
                               set_flags(exact=exact))
    return (utility, True), best_move


def alpha_beta_max(state, expanded_state, evaluate, remaining_depth,
                   alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs the max part of minimax search with alpha beta pruning, returning
    a ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to an
    alpha or a beta cutoff), and move is a move that will give a utility of
    <utility>. Note that <move> is None iff the given state is terminal, or
    'remaining_depth' starts off at 0.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :param alpha: the utility of the best (i.e. highest-utility) move found so
        far for the king player
    :type: alpha numeric
    :param beta: the utility of the best (i.e. lowest-utility) move found so
        far for the dragon player
    :type: beta numeric
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        return (value[SCORE_INDEX],
                is_exact(value[FLAGS_INDEX])), value[MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        exact = True
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        exact = True  # Since the evaluation is a number, not a cutoff.
        best_move = None
    else:
        # TODO: what if every successor is a dragon win? Then, will it return
        #       when exact == None and best_move == None? I think so.
        utility = DRAGON_WIN
        exact = None  # Not sure
        best_move = None  # Not sure
        for new_state, new_expanded_state, new_move in \
                successors(state, expanded_state):
            new_util, new_exact = \
                alpha_beta_min(new_state, new_expanded_state, evaluate,
                               remaining_depth - 1, alpha, beta)[0]
            if utility < new_util:
                utility = new_util
                best_move = new_move
                exact = new_exact
            if utility >= beta:
                return (utility, exact), best_move
            else:
                alpha = max(alpha, utility)
    return (utility, exact), best_move


def alpha_beta_min(state, expanded_state, evaluate, remaining_depth,
                   alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs the min part of minimax search with alpha beta pruning, returning
    a ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to an
    alpha or a beta cutoff), and move is a move that will give a utility of
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
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :param alpha: the utility of the best (i.e. highest-utility) move found so
        far for the king player
    :type: alpha numeric
    :param beta: the utility of the best (i.e. lowest-utility) move found so
        far for the dragon player
    :type: beta numeric
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        return (value[SCORE_INDEX],
                is_exact(value[FLAGS_INDEX])), value[MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        exact = True
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        utility = evaluate(state, expanded_state)
        exact = True  # Since the evaluation is a number, not a cutoff.
        best_move = None
    else:
        # TODO: what if every successor is a dragon win? Then, will it return
        #       when exact == None and best_move == None? I think so.
        utility = KING_WIN
        best_move = None  # Not sure
        exact = None  # Not sure
        for new_state, new_expanded_state, new_move in \
                successors(state, expanded_state):
            new_util, new_exact = \
                alpha_beta_max(new_state, new_expanded_state, evaluate,
                               remaining_depth - 1, alpha, beta)[0]
            if utility > new_util:
                utility = new_util
                best_move = new_move
                exact = new_exact
            if utility <= alpha:
                return (utility, exact), best_move
            else:
                beta = min(beta, utility)
    return (utility, exact), best_move


def alpha_beta(state, expanded_state, evaluate, remaining_depth):
    """
    Performs minimax search with alpha beta pruning, returning a
    ((<utility>, <exact>), <move>) pair, where <utility> is the utility of
    <move>, <exact> is True iff <utility> is an exact value (as opposed to an
    alpha or a beta cutoff), and move is a move that will give a utility of
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
    :param remaining_depth: how many more plies to visit recursively (i.e. what
        is the (maximum) remaining depth of the minimax recursive call tree);
        when this value hits 0, if the state at that depth is not a terminal
        state, the 'evaluate' function is applied to the state, instead of
        performing a recursive call to minimax
    :type remaining_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    if player_turn(state) == KING_PLAYER:
        return alpha_beta_max(state, expanded_state, evaluate, remaining_depth)
    else:
        return alpha_beta_min(state, expanded_state, evaluate, remaining_depth)
