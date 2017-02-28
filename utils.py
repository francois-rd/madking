from state import tile_index, KING_PLAYER

FILE = ['A', 'B', 'C', 'D', 'E']
RANK = ['5', '4', '3', '2', '1']


def parse_move(str_move):
    """
    Parses a move given in a format similar to 'A2B3', which means "move the
    piece at tile 'A2' to tile 'B3'", into a <from-tile-index> and a
    <to-tile-index>. Returns the (True, <from-tile-index>, <to-tile-index>) if
    the move is correctly formatted, and (False, -1, -1) otherwise.

    :param str_move: a move given in a format similar to 'A2B3'
    :type str_move: string
    :return: the (True, <from-tile-index>, <to-tile-index>) if the move is
        correctly formatted, and (False, -1, -1) otherwise
    :rtype: (bool, int, int)
    """
    if len(str_move) != 4 or \
            str_move[0] not in FILE or str_move[1] not in RANK or \
            str_move[2] not in FILE or str_move[3] not in RANK:
        return False, -1, -1
    return True, tile_index(str_move[0:2]), tile_index(str_move[2:4])


def record_move_data(search, evaluate, max_depth, move_number, player, time):
    """
    Records the given data, as well as all the counters in the
    TranspositionTable and the search algorithms, to a file called
    "data.tmp.csv". Then, resets all the counters.

    :param search: a search function taking a state, an expanded state, an
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param move_number: the count of the moves so far in the game
    :type move_number: int
    :param player: the integer ID of the current player
    :type player: int
    :param time: the time taken for the search
    :type time: float
    """
    from minimax import get_table_metadata_and_global_counters_then_reset
    data = [search.__name__, evaluate.__name__, max_depth, move_number,
            "king" if player == KING_PLAYER else "dragon", time,
            *get_table_metadata_and_global_counters_then_reset()]
    with open("data.tmp.csv", "a") as file:
        print(','.join(str(i) for i in data), file=file)
