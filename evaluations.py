from state import *


def simple_eval(state, expanded_state):
    """
    Returns a heuristic estimate of the utility value of the given state,
    according to the rule that the utility should be positive when the board
    is in favour of  the king player, and negative when it is in favour of the
    dragon player.

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
    controlled_tiles = get_count_controlled_tiles(expanded_state)
    threatened_units = get_count_threatened_units(state, expanded_state)
    king_pos = get_king_tile_index(state)
    king_threat = get_king_risk_level(king_pos, expanded_state)
    king_prog = get_king_progress(king_pos)
    score = (guard_piece_score - dragon_piece_score) + \
        controlled_tiles + \
        threatened_units + \
        king_prog + \
        king_threat
    return score


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


def get_count_controlled_tiles(expanded_state):
    """
    Return the number of tiles controlled by the king player minus the number
    of tiles controlled by the dragon player. This value can be scaled to true
    win and loss utility values.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the difference in the number of tiles controlled by the king
        player and the dragon player
    :rtype: int
    """    
    controlled_tiles = 0
    # Add one for every tile under KING control.
    # Subtract one for every tile under DRAGON control.
    # At the end, there will be an integer representing the relative advantage
    # (or disadvantage, if negative) of the king player over the dragon player.
    for tile in range(BOARD_NUM_RANKS * BOARD_NUM_FILES):
        content = expanded_state[tile]
        if content == EMPTY:
            neighbours = get_orthogonal_tiles_around(tile)
            surrounding_p1_units = 0
            surrounding_p2_units = 0
            for tile_number in neighbours:
                neighbour_content = expanded_state[tile_number]
                if neighbour_content == GUARD or neighbour_content == KING:
                    surrounding_p1_units += 1
                elif neighbour_content == DRAGON:
                    surrounding_p2_units += 1
            if surrounding_p1_units >= 2:
                controlled_tiles += 1
            elif surrounding_p2_units >= 3:
                controlled_tiles -= 1
    return controlled_tiles


def get_count_threatened_units(state, expanded_state):
    """
    Return the number of dragons threatened to be captured by the king player
    minus the number guards threatened to be captured by the dragon player.
    This value can be scaled to true win and loss utility values.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: the difference in the number of units threatened by the king
        player and the dragon player
    :rtype: int
    """
    dragon_positions = get_live_dragon_enumeration(state)
    count_threatened_tiles = 0
    for _, dragon in dragon_positions:
        threats = 0
        neighbour_tiles = get_orthogonal_tiles_around(dragon-DRAGON_BASE)
        for neighbour in neighbour_tiles:
            content = expanded_state[neighbour]
            if content == GUARD or content == KING:
                threats += 1
        if threats >= 2:
            count_threatened_tiles += 1

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
                unoccupied_neighbours = \
                    [i for i in guard_neighbours if i not in used_positions]
                for unoccupied_tile in unoccupied_neighbours:
                    second_neighbours = \
                        get_orthogonal_tiles_around(unoccupied_tile)
                    second_neighbours.extend(
                        get_diagonal_tiles_around(unoccupied_tile))
                    for n in second_neighbours:
                        content = expanded_state[n]
                        # Increase the threat if there is a dragon on one
                        # of the neighbouring tiles, but only if the tile
                        # of interest is not on which has already been seen.
                        if n not in used_positions and content == DRAGON:
                            threats += 1
        if threats >= 3:
            count_threatened_tiles -= 1
    return count_threatened_tiles


def get_king_risk_level(king_tile_idx, expanded_state):
    """
    Returns an integer (possibly negative) indicating the risk level of the
    king. The smaller the value, the more risk for the king, and the better for
    the dragon player.
    
    :param king_tile_idx: A number 0-24 indicating the placement of the
        king on the board:
    :type king_tile_idx: int
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: an integer indicating the level of risk for the king
    :rtype: int
    """
    surrounding_tiles = get_orthogonal_tiles_around(king_tile_idx)
    surrounding_tiles.extend(get_diagonal_tiles_around(king_tile_idx))
    num_dragons = sum(expanded_state[i] == DRAGON for i in surrounding_tiles)
    num_guards = sum(expanded_state[i] == GUARD for i in surrounding_tiles)
    return num_guards - num_dragons


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
    controlled_tiles = get_count_controlled_tiles(expanded_state)
    print("controlled_tiles:", controlled_tiles)
    threatened_units = get_count_threatened_units(state, expanded_state)
    print("threatened_units:", threatened_units)
    king_pos = get_king_tile_index(state)
    king_prog = get_king_progress(king_pos)
    print("king_prog:", king_prog)
    print("total: ", guard_score - dragon_score + controlled_tiles + king_prog)
    print("value of simple_eval() on initial game state:",
          simple_eval(state, expanded_state))


if __name__ == "__main__":
    # If the code in _test() was directly here, it causes variable name
    # shadowing in some of the functions above, which is poor style.
    _test()
