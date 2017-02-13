from state import *

table = dict()  # mapping between states and (utility, move) pairs
DEFAULT_DEPTH_LIMIT = 100


def minimax(state, expanded_state, evaluate, remaining_depth):
    """
    Performs minimax search, returning a (<utility>, <move>) pair.

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
    :rtype: (numeric, (<from-tile-index>, <to-tile-index>))
    """
    global table

    print("New state with remaining depth", remaining_depth)

    # TODO: what about hash collisions?
    # TODO: what about checking the depth in the table... will need a fancier
    #       table eventually.
    hash_string = hash_state(state)
    if hash_string in table:
        print("In table!")
        return table[hash_string]

    is_term, utility = is_terminal(state, expanded_state)
    if is_term:
        print("Found terminal state!")
        best_move = None
    elif remaining_depth == 0:
        utility = evaluate(state, expanded_state)
        best_move = None
    else:
        print("Getting successors!")
        vs = [(minimax(new_state, new_expanded_state, evaluate,
                       remaining_depth - 1)[0], new_move) for
              new_state, new_expanded_state, new_move in
              successors(state, expanded_state)]
        print(vs)
        if player_turn(state) == KING_PLAYER:
            print("King's turn!")
            utility, best_move = max(vs, key=lambda i: i[0])
        else:
            print("Dragons turn!")
            utility, best_move = min(vs, key=lambda i: i[0])
    print("Putting it in the table!")
    table[hash_string] = (utility, best_move)
    return utility, best_move


if __name__ == "__main__":
    from evaluations import simple_eval

    game_state = get_default_game_start()
    game_expanded_state = create_expanded_state_representation(game_state)
    u, m = minimax(game_state, game_expanded_state, simple_eval,
                   DEFAULT_DEPTH_LIMIT)
    print("Final:", u, m)
