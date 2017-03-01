from state import *


def simple_eval(state, expanded_state):
    """
    Returns a heuristic estimate of the utility value of the given state,
    according to the rule that the utility should be positive when the board
    is in favour of  the king player, and negative when it is in favour of the
    dragon player.

    Utility = Sum((King_feature - Dragon_feature) * weight)

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a heuristic estimate of the utility value of the given state
    :rtype: numeric
    """
    king_value = 0
    dragon_weight = 1
    guard_weight = 5 / 4
    num_dragons = len(get_live_dragon_enumeration(state))
    num_guards = len(get_live_guards_enumeration(state))
    dragon_piece_score = num_dragons * dragon_weight
    guard_piece_score = round(num_guards * guard_weight) + king_value
    controlled_tiles = get_king_controlled_tiles(expanded_state) - \
        get_dragon_controlled_tiles(expanded_state)
    threatened_units = get_dragon_threatened(state, expanded_state) - \
        get_guard_threatened(state, expanded_state)
    king_pos = get_king_tile_index(state)
    king_threat = get_king_risk_level(state, expanded_state, king_pos)
    king_prog = get_king_progress(king_pos)
    score = (guard_piece_score - dragon_piece_score) + \
        controlled_tiles + \
        threatened_units + \
        king_prog + \
        king_threat
    return score


def split_weight_eval(state, expanded_state):
    """
    Returns a heuristic estimate of the utility value of the given state,
    according to the rule that the utility should be positive when the board
    is in favour of the king player, and negative when it is in favour of the
    dragon player.

    Utility = Sum(King_feature * weight) - Sum(Dragon_feature * weight)
    
    :param state: the current state for evaluation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte,char)
    :return: a heuristic estimate of the utility value of the given state
    :rtyep: a numeric value   
    """
    return get_king_features(state, expanded_state) - \
        get_dragon_features(state, expanded_state)


def get_king_features(state, expanded_state):
    """
    Returns a weighted sum of king features: Sum(King_feature * weight).

    List of KING features:
        GUARDS alive,
        KING progress,
        KING controlled tiles,
        threatened DRAGONS by GUARD and KING,
        KING risk level,
        threatened GUARDS by DRAGONS.
    Each feature is multiplied by a specific weight. The return value is the
    sum of each feature times its weight.

    :param state: the current state for evaluation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte,char)
    :return: an estimated utility value for the king player of the given state
    :rtype: numeric
    """
    w_guard_alive = 4
    w_king_progress = 10
    w_king_controlled_tiles = 1
    w_dragon_threatened = 2
    w_king_risk_level = -10  # Negative because this is bad for the king player.
    w_guard_threatened = -3  # Negative because this is bad for the king player.
    king_pos = get_king_tile_index(state)
    return (w_guard_alive * len(get_live_guards_enumeration(state))
            + (w_king_progress * get_king_progress(king_pos))
            + (w_king_controlled_tiles *
                get_king_controlled_tiles(expanded_state))
            + (w_dragon_threatened *
                get_dragon_threatened(state, expanded_state))
            + (w_king_risk_level *
                get_king_risk_level(state, expanded_state, king_pos))
            + (w_guard_threatened *
                get_guard_threatened(state, expanded_state)))


def get_dragon_features(state, expanded_state):
    """
    Returns a weighted sum of dragon features: Sum(Dragon_feature * weight).

    List of DRAGON features:
        DRAGONS alive,
        DRAGON controlled tiles,
        threatened DRAGONS by GUARD and KING,
        KING risk level,
        threatened GUARDS by DRAGONS.
    Each feature is multiplied by a specific weight. The return value is the
    sum of each feature times its weight.

    :param state: the current state for evaluation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte,char)
    :return: an estimated utility value for the dragon player of the given state
    :rtype: numeric
    
    """
    w_dragon_alive = 8
    w_dragon_controlled_tiles = 1
    w_dragon_threatened = -9  # Neg., because this is bad for the dragon player.
    w_king_risk_level = 10
    w_guard_threatened = 4
    w_king_progress = -10  # Neg., because this is bad for the dragon player.
    king_pos = get_king_tile_index(state)
    return (w_dragon_alive * len(get_live_dragon_enumeration(state))
            + (w_dragon_controlled_tiles *
                get_dragon_controlled_tiles(expanded_state))
            + (w_dragon_threatened *
                get_dragon_threatened(state, expanded_state))
            + (w_king_risk_level *
                get_king_risk_level(state, expanded_state, king_pos))
            + (w_guard_threatened *
                get_guard_threatened(state, expanded_state))
            + (w_king_progress * get_king_progress(king_pos)))


def get_orthogonal_tiles_around(tile_idx):
    """
    Returns a list of the tile indices of the four neighbouring tiles
    orthogonal to the tile at the given index, if they are on the board.
    
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of the tile indices of the four orthogonal tiles
    :rtype: list(byte)
    """
    tiles = []
    left = tile_idx - BOARD_NUM_RANKS
    right = tile_idx + BOARD_NUM_RANKS
    above = tile_idx + 1
    below = tile_idx - 1
    if left >= 0:
        tiles.append(left)
    if right < BOARD_NUM_RANKS * BOARD_NUM_FILES:
        tiles.append(right)
    if above % BOARD_NUM_RANKS != 0:
        tiles.append(above)
    if tile_idx % BOARD_NUM_RANKS != 0:  # tile_idx, not below!
        tiles.append(below)
    return tiles


def get_diagonal_tiles_around(tile_idx):
    """
    Returns a list of the tile indices of the four neighbouring tiles
    diagonal to the tile at the given index, if they are on the board.
    
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of the tile indices of the four diagonal tiles
    :rtype: list(byte)
    """
    tiles = []
    left = tile_idx - BOARD_NUM_RANKS
    if left >= 0:  # If left is on the board.
        upper_left = left + 1
        lower_left = left - 1
        if upper_left % BOARD_NUM_RANKS != 0:
            tiles.append(upper_left)
        if left % BOARD_NUM_RANKS != 0:  # left, not lower_left!
            tiles.append(lower_left)
    right = tile_idx + BOARD_NUM_RANKS
    if right < BOARD_NUM_RANKS * BOARD_NUM_FILES:  # If right is on the board.
        upper_right = right + 1
        lower_right = right - 1
        if upper_right % BOARD_NUM_RANKS != 0:
            tiles.append(upper_right)
        if right % BOARD_NUM_RANKS != 0:  # right, not lower_right!
            tiles.append(lower_right)
    return tiles


def get_king_progress(king_tile_idx):
    """
    Returns a value that is representative of the King's progress towards the
    first rank of the board (i.e. towards winning the game for the king
    player). This is an integer between 0 and 4 (inclusive), which should be
    scaled for an accurate measurement.
    
    :param king_tile_idx: tile index (0-24) corresponding to the board
        position with the king
    :type king_tile_idx: byte
    :return: a value that is representative of the King's progress towards the
        first rank of the board
    :rtype: int
    """
    return (BOARD_NUM_RANKS - 1) - (king_tile_idx % BOARD_NUM_RANKS)


def get_king_controlled_tiles(expanded_state):
    """
    Returns the number of tiles controlled by the king player.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the number of tiles controlled by the king player
    :rtype: int
    """
    controlled_tiles = 0
    for tile in range(BOARD_NUM_RANKS * BOARD_NUM_FILES):
        content = expanded_state[tile]
        if content == EMPTY:
            neighbours = get_orthogonal_tiles_around(tile)
            surrounding_p1_units = 0
            for tile_number in neighbours:
                neighbour_content = expanded_state[tile_number]
                if neighbour_content == GUARD or neighbour_content == KING:
                    surrounding_p1_units += 1
            if surrounding_p1_units >= 2:
                controlled_tiles += 1
    return controlled_tiles


def get_dragon_controlled_tiles(expanded_state):
    """
    Returns the number of tiles controlled by the dragon player.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the number of tiles controlled by the dragon player
    :rtype: int
    """
    controlled_tiles = 0
    for tile in range(BOARD_NUM_RANKS * BOARD_NUM_FILES):
        content = expanded_state[tile]
        if content == EMPTY:
            neighbours = get_orthogonal_tiles_around(tile)
            surrounding_p2_units = 0
            for tile_number in neighbours:
                neighbour_content = expanded_state[tile_number]
                if neighbour_content == DRAGON:
                    surrounding_p2_units += 1
            if surrounding_p2_units >= 3:
                controlled_tiles += 1
    return controlled_tiles


def get_dragon_threatened(state, expanded_state):
    """
    Returns the number of DRAGONS threatened to be captured by the king player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the number of DRAGONS threatened to be captured by the king player
    :rtype: int
    """
    count_threatened_tiles = 0
    dragon_positions = get_live_dragon_enumeration(state)
    for _, dragon in dragon_positions:
        threats = 0
        neighbour_tiles = get_orthogonal_tiles_around(dragon-DRAGON_BASE)
        for neighbour in neighbour_tiles:
            content = expanded_state[neighbour]
            if content == GUARD or content == KING:
                threats += 1
        if threats >= 2:
            count_threatened_tiles += 1
    return count_threatened_tiles


def get_guard_threatened(state, expanded_state):
    """
    Returns the number of GUARDS threatened to be captured by the dragon player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the number of GUARDS threatened to be captured by the dragon player
    :rtype: int
    """
    count_threatened_tiles = 0
    guard_positions = get_live_guards_enumeration(state)
    for _, guard in guard_positions:
        threats = 0
        used_positions = []
        guard_neighbours = get_orthogonal_tiles_around(guard)
        # Examine all direct neighbour of this guard.
        for neighbour in guard_neighbours:
            content = expanded_state[neighbour]
            if content == DRAGON:
                threats += 1
                used_positions.append(neighbour)
            elif content == KING or content == GUARD:
                used_positions.append(neighbour)
            # If there are exactly 2 threats, we need to consider if a third
            # dragon could move into the spot on the next turn.  If there are
            # fewer than 2 dragons, there is no way this guard could be
            # captured in the next turn, so move on to the next guard.
            if threats == 2:
                unoccuppied_neighbours = \
                        [i for i in guard_neighbours if i not in used_positions]
                for unoccuppied_tile in unoccuppied_neighbours:
                    second_neighbours = \
                            get_orthogonal_tiles_around(unoccuppied_tile)
                    second_neighbours.extend(
                            get_diagonal_tiles_around(unoccuppied_tile))
                    for n in second_neighbours:
                        content = expanded_state[n]
                        # Increase the threat if there is a dragon on one
                        # of the neighbouring tiles, but only if the tile
                        # of interest is not on which has already been seen.
                        if n not in used_positions and content == DRAGON:
                            threats += 1
        if threats >= 3:
            count_threatened_tiles += 1
    return count_threatened_tiles


def get_king_risk_level(state, expanded_state, king_tile_idx):
    """
    Returns an integer (possibly negative) indicating the risk level of the
    king. The smaller the value, the more risk for the king, and the better for
    the dragon player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_idx: A number 0-24 indicating the placement of the
        king on the board:
    :type king_tile_idx: int
    :return: an integer indicating the level of risk for the king
    :rtype: int

    surrounding_tiles = get_orthogonal_tiles_around(king_tile_idx)
    surrounding_tiles.extend(get_diagonal_tiles_around(king_tile_idx))
    num_dragons = sum(expanded_state[i] == DRAGON for i in surrounding_tiles)
    num_guards = sum(expanded_state[i] == GUARD for i in surrounding_tiles)
    return num_guards - num_dragons
    """
    # Currently, king_risk_level is calculated by the number of possible moves
    # that KING can make. If the KING is surrounded by DRAGONS, he will have
    # fewer possible moves.

    #not implemented correctly, just return 0 for now
    return 0

    #return count_king_moves(state, expanded_state, king_tile_idx)


def _test():
    """
    Tests the functions in this file on the initial game state.
    """
    print("testing")
    state = DEFAULT_INITIAL_STATE
    expanded_state = create_expanded_state_representation(state)
    num_dragons = len(get_live_dragon_enumeration(state))
    num_guards = len(get_live_guards_enumeration(state))
    guard_weight = 5 / 4
    dragon_weight = 1
    king_value = 0
    dragon_score = num_dragons * dragon_weight
    guard_score = round(num_guards * guard_weight) + king_value
    controlled_tiles = get_king_controlled_tiles(expanded_state) - \
        get_dragon_controlled_tiles(expanded_state)
    print("controlled_tiles:", controlled_tiles)
    threatened_units = get_dragon_threatened(state, expanded_state) - \
        get_guard_threatened(state, expanded_state)
    print("threatened_units:", threatened_units)
    king_pos = get_king_tile_index(state)
    king_prog = get_king_progress(king_pos)
    print("king_prog:", king_prog)
    print("total: ", guard_score - dragon_score + controlled_tiles + king_prog)
    print("value of simple_eval() on initial game state:",
          simple_eval(state, expanded_state))
    print("value of split_weight_eval() on initial game state:",
          split_weight_eval(state, expanded_state))

if __name__ == "__main__":
    # If the code in _test() was directly here, it causes variable name
    # shadowing in some of the functions above, which is poor style.
    _test()
