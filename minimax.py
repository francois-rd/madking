from TranspositionTable import TranspositionTable
from state import *

_DEFAULT_SIZE = 1000000
# TODO: is *from the current root* really going to work for us????
"""
Each table entry corresponds to one state of the game (in this context, a
'state' is a board position as well as which player's turn it is).

The table keys will be the hash strings returned by state.hash_state().
The table values will be tuples of the form:
    (<max-depth>, <depth>, <age>, <score>, <move>, <exact-alpha-or-beta>)
where
    <max-depth> is the maximum depth in plies *from the current root* to which
        the search algorithm will search
    <depth> is the depth in plies *from current root* of the corresponding
        state
    <age> is an age counter, which increases whenever a piece is captured
    <score> is the utility value of the corresponding state
    <move> is the move that leads to the best possible child state (i.e. the
        move that will lead to the value of <score> being correct)
    <exact-alpha-or-beta> is a byte, where
        the first lowest-order bit is set iff <score> is an exact value (as
            opposed to a heuristic estimate)
        the second lowest-order bit is set iff <score> is an (exact or
            heuristic estimate) alpha cutoff (for alpha beta minimax search)
        the third lowest-order bit is set iff <score> is an (exact or heuristic
            estimate) beta cutoff (for alpha beta minimax search)
"""
_table = TranspositionTable(_DEFAULT_SIZE, TranspositionTable.always_replace)

_MAX_DEPTH_INDEX = 0
_DEPTH_INDEX = 1
_AGE_INDEX = 2
_SCORE_INDEX = 3
_MOVE_INDEX = 4
_EXACT_ALPHA_BETA_INDEX = 5

_EXACT_MASK = 0b00000001
_ALPHA_MASK = 0b00000010
_BETA_MASK = 0b00000100

DEFAULT_DEPTH_LIMIT = 4


def _is_exact(exact_alpha_or_beta):
    """
    Returns True iff the "exact" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "exact" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _EXACT_MASK)


def _is_alpha_cutoff(exact_alpha_or_beta):
    """
    Returns True iff the "alpha cutoff" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "alpha cutoff" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _ALPHA_MASK)


def _is_beta_cutoff(exact_alpha_or_beta):
    """
    Returns True iff the "beta cutoff" bit of 'exact_alpha_or_beta' is set.

    :param exact_alpha_or_beta: the <exact-alpha-or-beta> field of a
        TranspositionTable value
    :type exact_alpha_or_beta: byte
    :return: True iff the "beta cutoff" bit of 'exact_alpha_or_beta' is set
    :rtype: bool
    """
    return bool(exact_alpha_or_beta & _BETA_MASK)


def minimax(state, expanded_state, evaluate, age, remaining_depth, max_depth):
    """
    Performs minimax search, returning a ((<utility>, <exact>), <move>) pair,
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
    :param max_depth: the maximum depth to which the minimax search will go;
        used to produce depth-unique hash values of states for the table
    :type max_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    global _table
    # We calculate the current depth of the search by subtracting the 
    # remaining depth from the maximum depth.  Where the remaining depth is
    # 0, we will be 'max_depth' down the search tree.
    hash_string = hash_state(state)
    value = _table.get(hash_string)
    if value is not None and value[_MAX_DEPTH_INDEX] >= max_depth and \
            value[_DEPTH_INDEX] >= max_depth - remaining_depth and \
            value[_AGE_INDEX] >= age:
        return (value[_SCORE_INDEX],
                _is_exact(value[_EXACT_ALPHA_BETA_INDEX])), value[_MOVE_INDEX]
    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        exact = True
        best_move = None
    elif remaining_depth == 0:
        utility = evaluate(state, expanded_state)
        exact = False
        best_move = None
    else:
        vs = [(minimax(new_state, new_expanded_state, evaluate, age,
                       remaining_depth - 1, max_depth)[0], new_move) for
              new_state, new_expanded_state, new_move in
              successors(state, expanded_state)]
        if player_turn(state) == KING_PLAYER:
            (utility, exact), best_move = max(vs, key=lambda i: i[0][0])
        else:
            (utility, exact), best_move = min(vs, key=lambda i: i[0][0])
        _table[hash_string] = (max_depth, max_depth - remaining_depth, age,
                               utility, best_move, exact)
    return (utility, exact), best_move


def alpha_beta(state, expanded_state, evaluate, age, remaining_depth,
               max_depth):
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
    :param max_depth: the maximum depth to which the minimax search will go;
        used to produce depth-unique hash values of states for the table
    :type max_depth: int
    :return: a ((<utility>, <exact>), <move>) pair
    :rtype: ((numeric, bool), (byte, byte))
    """
    pass


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
                   depth_limit, depth_limit)
    with open("minimax_depth_" + str(depth_limit) + ".json", 'w') as outfile:
        json.dump(_table.to_json_serializable(), outfile, indent=4)
    print("Final:", u, m)
