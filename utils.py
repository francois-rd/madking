from state import tile_index

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


def record_move_search_time(time, evaluate, search, max_depth):
    """
    Records the given time to the "timing.csv" file, along with the
    corresponding evaluation function, search algorithm, and maximum search
    depth.

    :param time: the time taken for the search
    :type time: float
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    """
    with open("timing.csv", "a") as file:
        file.write(','.join(str(i) for i in [time, evaluate.__name__,
                                             search.__name__, max_depth]))
