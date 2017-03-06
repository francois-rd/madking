from TranspositionTable import *
from state import *

_table = None
DEFAULT_DEPTH_LIMIT = 4

# For minimax and alpha beta.
num_term = 0
num_leafs = 0
num_usable_hits = 0

# For alpha beta only.
num_usable_hits_exact = 0
num_usable_hits_alpha = 0
num_usable_hits_beta = 0
num_usable_hits_pruning = 0
num_move_ordering_alpha_cutoff = 0
num_move_ordering_beta_cutoff = 0
num_alpha_cutoff = 0
num_beta_cutoff = 0


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


def get_table_count():
    """
    Returns the length of the global transposition table.

    :return: the length of the global transposition table
    :rtype: int
    """
    global _table
    return len(_table)


def get_table_metadata_and_global_counters_then_reset():
    """
    Returns a list containing all the metadata of the global TranspositionTable
    and all the global counters used by minimax and alpha beta search, then
    resets all of these.

    :return: a list containing all the counters
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    global num_usable_hits_exact
    global num_usable_hits_alpha
    global num_usable_hits_beta
    global num_usable_hits_pruning
    global num_move_ordering_alpha_cutoff
    global num_move_ordering_beta_cutoff
    global num_alpha_cutoff
    global num_beta_cutoff
    counters = [_table.get_replacement_policy().__name__, _table.get_max_size(),
                get_table_count(), *_table.get_counters(), num_term, num_leafs,
                num_usable_hits, num_usable_hits_exact, num_usable_hits_alpha,
                num_usable_hits_beta, num_usable_hits_pruning,
                num_move_ordering_alpha_cutoff, num_move_ordering_beta_cutoff,
                num_alpha_cutoff, num_beta_cutoff]
    _table.reset_counters()
    num_term = 0
    num_leafs = 0
    num_usable_hits = 0
    num_usable_hits_exact = 0
    num_usable_hits_alpha = 0
    num_usable_hits_beta = 0
    num_usable_hits_pruning = 0
    num_move_ordering_alpha_cutoff = 0
    num_move_ordering_beta_cutoff = 0
    num_alpha_cutoff = 0
    num_beta_cutoff = 0
    return counters


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


def print_utility_move_and_global_counters(result):
    """
    Prints the given result of minimax or alpha beta search, as well as the
    global counters 'num_term', 'num_leafs', and 'num_usable_hits'.

    :param result: a (<utility>, <move>) pair returned by either minimax or
        alpha beta
    :type result: (numeric, (byte, byte))
    """
    global num_term
    global num_leafs
    global num_usable_hits
    global num_usable_hits_exact
    global num_usable_hits_alpha
    global num_usable_hits_beta
    global num_usable_hits_pruning
    global num_move_ordering_alpha_cutoff
    global num_move_ordering_beta_cutoff
    global num_alpha_cutoff
    global num_beta_cutoff
    print("Final:", "utility", result[0], "move", result[1], "terminal",
          num_term, "leafs", num_leafs, "usable_hits", num_usable_hits)
    print("For alpha beta only:", "usable_hits_exact", num_usable_hits_exact,
          "usable_hits_alpha", num_usable_hits_alpha, "usable_hits_beta",
          num_usable_hits_beta, "usable_hits_pruning", num_usable_hits_pruning,
          "move_ordering_alpha_cutoff", num_move_ordering_alpha_cutoff,
          "move_ordering_beta_cutoff", num_move_ordering_beta_cutoff,
          "alpha_cutoff", num_alpha_cutoff, "beta_cutoff", num_beta_cutoff)


def minimax(state, expanded_state, evaluate, remaining_depth):
    """
    Performs minimax search, returning a (<utility>, <move>) pair, where
    <utility> is the utility of <move>, and <move> is one of the moves that
    will give a utility of <utility>. Note that <move> is None iff the given
    state is terminal, or 'remaining_depth' starts off at 0.

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
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        return value[SCORE_INDEX], value[MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        best_move = None
        if is_piece_threatened(state, expanded_state) or \
                can_king_win(state, expanded_state):
            utility = quiescence_search(state, expanded_state, evaluate)
        else:
            utility = evaluate(state, expanded_state)
    else:
        vs = [(minimax(new_state, new_expanded_state, evaluate,
                       remaining_depth - 1)[0], new_move) for
              new_state, new_expanded_state, new_move in
              successors(state, expanded_state)]
        if player_turn(state) == KING_PLAYER:
            utility, best_move = max(vs, key=lambda i: i[0])
        else:
            utility, best_move = min(vs, key=lambda i: i[0])
        _table[hash_string] = (remaining_depth, utility, best_move, EXACT)
    return utility, best_move


def minimax_ordered(state, expanded_state, evaluate, remaining_depth):
    """
    Performs minimax search, returning a (<utility>, <move>) pair, where
    <utility> is the utility of <move>, and <move> is one of the moves that
    will give a utility of <utility>. Note that <move> is None iff the given
    state is terminal, or 'remaining_depth' starts off at 0.

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
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        return value[SCORE_INDEX], value[MOVE_INDEX]
    is_term, utility = is_terminal_ordered(state, expanded_state)
    if is_term:
        num_term += 1
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        best_move = None
        if is_piece_threatened(state, expanded_state) or \
                can_king_win(state, expanded_state):
            utility = quiescence_search_ordered(state, expanded_state, evaluate)
        else:
            utility = evaluate(state, expanded_state)
    else:
        vs = [(minimax_ordered(new_state, new_expanded_state, evaluate,
                               remaining_depth - 1)[0], new_move) for
              new_state, new_expanded_state, new_move in
              successors_ordered(state, expanded_state)]
        if player_turn(state) == KING_PLAYER:
            utility, best_move = max(vs, key=lambda i: i[0])
        else:
            utility, best_move = min(vs, key=lambda i: i[0])
        _table[hash_string] = (remaining_depth, utility, best_move, EXACT)
    return utility, best_move


def alpha_beta(state, expanded_state, evaluate, remaining_depth,
               alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs minimax search with alpha beta pruning, returning a
    (<utility>, <move>) pair, where <utility> is the utility of <move>, and
    move is one of the moves that will give a utility of <utility>. Note that
    <move> is None iff the given state is terminal, or remaining_depth starts
    off at 0.

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
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    global num_usable_hits_exact
    global num_usable_hits_alpha
    global num_usable_hits_beta
    global num_usable_hits_pruning
    global num_move_ordering_alpha_cutoff
    global num_move_ordering_beta_cutoff
    global num_alpha_cutoff
    global num_beta_cutoff
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        flags = value[FLAGS_INDEX]
        score = value[SCORE_INDEX]
        if flags == EXACT:
            num_usable_hits_exact += 1
            return score, value[MOVE_INDEX]  # Is fail-hard because of EXACT.
        if flags == ALPHA_CUTOFF:
            num_usable_hits_alpha += 1
            alpha = max(alpha, score)
        if flags == BETA_CUTOFF:
            num_usable_hits_beta += 1
            beta = min(beta, score)
        if alpha >= beta:
            num_usable_hits_pruning += 1
            return score, value[MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        num_term += 1
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        best_move = None
        if is_piece_threatened(state, expanded_state) or \
                can_king_win(state, expanded_state):
            utility = quiescence_search_alpha_beta(state, expanded_state,
                                                   evaluate, alpha, beta)
        else:
            utility = evaluate(state, expanded_state)
    else:
        # Examine the stored move first. If it leads to an alpha or a beta
        # cutoff, we don't need to evaluate any of the other successors!
        utility = stored_move = best_move = None
        is_max = player_turn(state) == KING_PLAYER
        if value is not None:
            stored_move = best_move = value[MOVE_INDEX]
            stored_state = copy.deepcopy(state)
            stored_expanded_state = \
                create_expanded_state_representation(stored_state)
            move_piece(stored_state, stored_expanded_state, best_move[0],
                       best_move[1])
            utility = alpha_beta(stored_state, stored_expanded_state, evaluate,
                                 remaining_depth - 1, alpha, beta)[0]
            if is_max:
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_move_ordering_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:  # Might still help narrow the search window.
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_move_ordering_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:  # Might still help narrow the search window.
                    beta = min(beta, utility)
        # Initialize utility and best_move either with first successor if there
        # was no stored move.
        _successors = successors(state, expanded_state).__iter__()
        if stored_move is None:
            first_state, first_expanded_state, best_move = next(_successors)
            utility = alpha_beta(first_state, first_expanded_state, evaluate,
                                 remaining_depth - 1, alpha, beta)[0]
            if is_max:
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        # Go through the remaining successors to find the true best.
        for new_state, new_expanded_state, new_move in _successors:
            if stored_move is not None and new_move == stored_move:
                continue  # Skip the stored move, if there was one.
            new_util = alpha_beta(new_state, new_expanded_state, evaluate,
                                  remaining_depth - 1, alpha, beta)[0]
            if is_max:
                if utility < new_util:
                    utility = new_util
                    best_move = new_move
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                    best_move = new_move
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        # No earlier alpha or beta cutoff was possible. Check one last time.
        if utility <= alpha:
            flag = ALPHA_CUTOFF
        elif utility >= beta:
            flag = BETA_CUTOFF
        else:
            flag = EXACT
        _table[hash_string] = (remaining_depth, utility, best_move, flag)
    return utility, best_move


def alpha_beta_ordered(state, expanded_state, evaluate, remaining_depth,
                       alpha=DRAGON_WIN, beta=KING_WIN):
    """
    Performs minimax search with alpha beta pruning, returning a
    (<utility>, <move>) pair, where <utility> is the utility of <move>, and
    move is one of the moves that will give a utility of <utility>. Note that
    <move> is None iff the given state is terminal, or remaining_depth starts
    off at 0.

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
    :return: a (<utility>, <move>) pair
    :rtype: (numeric, (byte, byte))
    """
    global _table
    global num_term
    global num_leafs
    global num_usable_hits
    global num_usable_hits_exact
    global num_usable_hits_alpha
    global num_usable_hits_beta
    global num_usable_hits_pruning
    global num_move_ordering_alpha_cutoff
    global num_move_ordering_beta_cutoff
    global num_alpha_cutoff
    global num_beta_cutoff
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[DEPTH_INDEX] >= remaining_depth:
        num_usable_hits += 1
        flags = value[FLAGS_INDEX]
        score = value[SCORE_INDEX]
        if flags == EXACT:
            num_usable_hits_exact += 1
            return score, value[MOVE_INDEX]  # Is fail-hard because of EXACT.
        if flags == ALPHA_CUTOFF:
            num_usable_hits_alpha += 1
            alpha = max(alpha, score)
        if flags == BETA_CUTOFF:
            num_usable_hits_beta += 1
            beta = min(beta, score)
        if alpha >= beta:
            num_usable_hits_pruning += 1
            return score, value[MOVE_INDEX]
    is_term, utility = is_terminal_ordered(state, expanded_state)
    if is_term:
        num_term += 1
        best_move = None
    elif remaining_depth == 0:
        num_leafs += 1
        best_move = None
        if is_piece_threatened(state, expanded_state) or \
                can_king_win(state, expanded_state):
            utility = \
                quiescence_search_alpha_beta_ordered(state, expanded_state,
                                                     evaluate, alpha, beta)
        else:
            utility = evaluate(state, expanded_state)
    else:
        # Examine the stored move first. If it leads to an alpha or a beta
        # cutoff, we don't need to evaluate any of the other successors!
        utility = stored_move = best_move = None
        is_max = player_turn(state) == KING_PLAYER
        if value is not None:
            stored_move = best_move = value[MOVE_INDEX]
            stored_state = copy.deepcopy(state)
            stored_expanded_state = \
                create_expanded_state_representation(stored_state)
            move_piece(stored_state, stored_expanded_state, best_move[0],
                       best_move[1])
            utility = alpha_beta_ordered(stored_state, stored_expanded_state,
                                         evaluate, remaining_depth - 1, alpha,
                                         beta)[0]
            if is_max:
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_move_ordering_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:  # Might still help narrow the search window.
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_move_ordering_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:  # Might still help narrow the search window.
                    beta = min(beta, utility)
        # Initialize utility and best_move either with first successor if there
        # was no stored move.
        _successors = successors_ordered(state, expanded_state).__iter__()
        if stored_move is None:
            first_state, first_expanded_state, best_move = next(_successors)
            utility = alpha_beta_ordered(first_state, first_expanded_state,
                                         evaluate, remaining_depth - 1, alpha,
                                         beta)[0]
            if is_max:
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        # Go through the remaining successors to find the true best.
        for new_state, new_expanded_state, new_move in _successors:
            if stored_move is not None and new_move == stored_move:
                continue  # Skip the stored move, if there was one.
            new_util = alpha_beta_ordered(new_state, new_expanded_state,
                                          evaluate, remaining_depth - 1, alpha,
                                          beta)[0]
            if is_max:
                if utility < new_util:
                    utility = new_util
                    best_move = new_move
                if utility >= beta:  # Beta cutoff! Stop search early.
                    num_beta_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           BETA_CUTOFF)
                    return beta, best_move  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                    best_move = new_move
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    num_alpha_cutoff += 1
                    _table[hash_string] = (remaining_depth, utility, best_move,
                                           ALPHA_CUTOFF)
                    return alpha, best_move  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        # No earlier alpha or beta cutoff was possible. Check one last time.
        if utility <= alpha:
            flag = ALPHA_CUTOFF
        elif utility >= beta:
            flag = BETA_CUTOFF
        else:
            flag = EXACT
        _table[hash_string] = (remaining_depth, utility, best_move, flag)
    return utility, best_move


def quiescence_search(state, expanded_state, evaluate):
    """
    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :return: a (hopefully) better estimate of the state's utility than
        'evaluate' alone can do
    :rtype: numeric
    """
    utilities = []
    for new_state, new_expanded_state, _ in \
            successors_capture_only(state, expanded_state):
        is_term, utility = is_terminal(new_state, new_expanded_state)
        if is_term:
            utilities.append(utility) 
        elif is_piece_threatened(new_state, new_expanded_state) or \
                can_king_win(new_state, new_expanded_state):
            utility = quiescence_search(new_state, new_expanded_state,
                                        evaluate)
            utilities.append(utility)
        else:
            utility = evaluate(new_state, new_expanded_state)
            utilities.append(utility)

    if len(utilities) == 0:
        return evaluate(state, expanded_state)
    if player_turn(state) == KING_PLAYER:
        return max(utilities)
    else:
        return min(utilities)


def quiescence_search_ordered(state, expanded_state, evaluate):
    """
    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :return: a (hopefully) better estimate of the state's utility than
        'evaluate' alone can do
    :rtype: numeric
    """
    utilities = []
    for new_state, new_expanded_state, _ in \
            successors_capture_only_ordered(state, expanded_state):
        is_term, utility = is_terminal_ordered(new_state, new_expanded_state)
        if is_term:
            utilities.append(utility)
        elif is_piece_threatened(new_state, new_expanded_state) or \
                can_king_win(new_state, new_expanded_state):
            utility = quiescence_search_ordered(new_state, new_expanded_state,
                                                evaluate)
            utilities.append(utility)
        else:
            utility = evaluate(new_state, new_expanded_state)
            utilities.append(utility)

    if len(utilities) == 0:
        return evaluate(state, expanded_state)
    if player_turn(state) == KING_PLAYER:
        return max(utilities)
    else:
        return min(utilities)


def quiescence_search_alpha_beta(state, expanded_state, evaluate, alpha, beta):
    """
    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param alpha: the utility of the best (i.e. highest-utility) move found so
        far for the king player
    :type: alpha numeric
    :param beta: the utility of the best (i.e. lowest-utility) move found so
        far for the dragon player
    :type: beta numeric
    :return: a (hopefully) better estimate of the state's utility than
        'evaluate' alone can do
    :rtype: numeric
    """
    import sys
    is_max = player_turn(state) == KING_PLAYER
    _successors = successors_capture_only(state, expanded_state)
    utility = -sys.maxsize if is_max else sys.maxsize
    for new_state, new_expanded_state, _ in _successors:
        is_term, new_util = is_terminal(new_state, new_expanded_state)
        if is_term:
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        elif is_piece_threatened(new_state, new_expanded_state) or \
                can_king_win(new_state, new_expanded_state):
            utility = quiescence_search_alpha_beta(new_state,
                                                   new_expanded_state,
                                                   evaluate, alpha, beta)
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        else:
            utility = evaluate(new_state, new_expanded_state)
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
    if len(_successors) == 0:
        return evaluate(state, expanded_state)
    return utility


def quiescence_search_alpha_beta_ordered(state, expanded_state, evaluate,
                                         alpha, beta):
    """
    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param alpha: the utility of the best (i.e. highest-utility) move found so
        far for the king player
    :type: alpha numeric
    :param beta: the utility of the best (i.e. lowest-utility) move found so
        far for the dragon player
    :type: beta numeric
    :return: a (hopefully) better estimate of the state's utility than
        'evaluate' alone can do
    :rtype: numeric
    """
    import sys
    is_max = player_turn(state) == KING_PLAYER
    _successors = successors_capture_only_ordered(state, expanded_state)
    utility = -sys.maxsize if is_max else sys.maxsize
    for new_state, new_expanded_state, _ in _successors:
        is_term, new_util = is_terminal_ordered(new_state, new_expanded_state)
        if is_term:
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        elif is_piece_threatened(new_state, new_expanded_state) or \
                can_king_win(new_state, new_expanded_state):
            utility = \
                quiescence_search_alpha_beta_ordered(new_state,
                                                     new_expanded_state,
                                                     evaluate, alpha, beta)
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
        else:
            utility = evaluate(new_state, new_expanded_state)
            if is_max:
                if utility < new_util:
                    utility = new_util
                if utility >= beta:  # Beta cutoff! Stop search early.
                    return beta  # Return fail-hard 'beta' value.
                else:
                    alpha = max(alpha, utility)
            else:  # Is min.
                if utility > new_util:
                    utility = new_util
                if utility <= alpha:  # Alpha cutoff! Stop search early.
                    return alpha  # Return fail-hard 'alpha' value.
                else:
                    beta = min(beta, utility)
    if len(_successors) == 0:
        return evaluate(state, expanded_state)
    return utility
