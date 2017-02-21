from state import *


def simple_eval(state, expanded_state):
    """
    Returns a heuristic estimate of the utility value of the given state,
    according to the rule that the utility should be positive when the board
    is in favour of  the king player, and negative when it is in favour of the
    dragon player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: to match function signature; ignored in this
        implementation
    :return: a heuristic estimate of the utility value of the given state
    :rtype: int
    """
    king_value = 1
    num_dragons = len(get_live_dragon_enumeration(state))
    num_guards = len(get_live_guards_enumeration(state))
    guard_weight = 5 / 4
    dragon_weight = 1
    dragon_piece_score = num_dragons * dragon_weight
    guard_piece_score = round(num_guards * guard_weight) + king_value
    controlled_tiles = get_count_controlled_tiles(expanded_state)
    threatened_units = get_count_threatened_units(state, expanded_state)
    king_threat = get_king_risk_level(expanded_state)
    king_pos = get_king_tile_index(state)
    king_prog = get_king_progress(king_pos)
    score = (guard_piece_score - dragon_piece_score) + \
        controlled_tiles + \
        threatened_tiles + \
        king_prog + \
        king_threat
    return score

def get_orthogonal_tiles_around(pos):
    """
    Get the numbers' of the neighbouring four orthognal tiles around the 
    board index 'pos'.
    
    :param pos: the board position of interest, 0-24
    :type pos: int
    :return: The number of tiles around the position 'pos'.
    :rtype: [int]
    """
    tiles = []
    left = pos - BOARD_NUM_RANKS
    right = pos + BOARD_NUM_RANKS
    above = pos + 1
    below = pos - 1
    size = BOARD_NUM_RANKS * BOARD_NUM_FILES
    if left < size and left >= 0:
        tiles.append(left)
    if right < size and right >= 0:
        tiles.append(right)
    if above % BOARD_NUM_RANKS != 0:
        tiles.append(above)
    if pos % BOARD_NUM_RANKS != 0:
        tiles.append(below)
    return tiles

def get_diagonal_tiles_around(pos):
    """
    Get the four diagonal  neighbouring indices of the board index 'pos'.  
    The values calculated for the upper right, upper left, lower right and 
    lower left indices are not currently guaranteed to work with variable 
    board sizes.
    
    :param pos: the board index of interest.
    :type pos: int
    :return: a list of integer containing index of board positions
    :rtype: [int]
    """
    tiles = []
    upper_left = pos - (BOARD_NUM_RANKS-1)
    upper_right = pos + (BOARD_NUM_RANKS+1)
    lower_left = pos - (BOARD_NUM_RANKS+1)
    lower_right = pos + (BOARD_NUM_RANKS-1)
    size = BOARD_NUM_RANKS * BOARD_NUM_FILES
    if upper_left % BOARD_NUM_RANKS != 0 and upper_left >= 0:
        tiles.append(upper_left)
    if upper_right % BOARD_NUM_RANKS != 0 and upper_right < size:
        tiles.append(upper_right)
    if lower_left >  0 and lower_left % BOARD_NUM_RANKS != 4:
        tiles.append(lower_left)
    if lower_right % BOARD_NUM_RANKS != 4 and lower_right < size:
        tiles.append(lower_right)
    return tiles


def get_king_progress(king_pos):
    """
    Return a value which is representative of the King's 
    progress to the end of the board - winning the game.
    This is a number from 0-4 which should be scaled 
    for an accurate measurement.
    
    :param king_pos: The King piece's position on the board.
    :type king_pos: int
    :return: A value representing the utility of the king's
        progress on the board, from 0 to 4.
    :rtype: int
    """
    return abs((king_pos % 5) - 4)


def get_count_controlled_tiles(expanded_state):
    """
    Return the number of tiles controlled by Player 1
    minus the number of tiles controlled by Player 2.
    This value can be scaled to true win and loss
    utility values.

    :param state: A compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: The difference in the number of controlled tiles 
        by Player 1 and Player 2.
    :rtype: int
    """    
    controlled_tiles = 0
    # Add one for every tile under KING control, 
    # and subtract one for every tile under DRAGON control.
    # At the end, there will be an integer representing
    # the relative advantage of one team over the other.
    for tile in range(BOARD_NUM_RANKS * BOARD_NUM_FILES):
        content = expanded_state[tile]
        if content is EMPTY:
            neighbours = get_orthogonal_tiles_around(tile)
            surrounding_p1_units = 0
            surrounding_p2_units = 0
            for tile_number in neighbours:
                neighbour_content = expanded_state[tile_number]
                if neighbour_content is GUARD:
                    surrounding_p1_units += 1
                elif neighbour_content is KING:
                    surrounding_p1_units += 1
                elif neighbour_content is DRAGON:
                    surrounding_p2_units += 1
            if surrounding_p1_units >= 2:
                controlled_tiles += 1
            elif surrounding_p2_units >= 3:
                controlled_tiles -= 1
    return controlled_tiles


def get_count_threatened_units(state, expanded_state):
    dragon_positions = get_live_dragon_enumeration(state)
    count_threatened_tiles = 0
    for dragon in dragon_positions:
        threats = 0
        neighbour_tiles = get_orthogonal_tiles_around(dragon[1]-DRAGON_BASE)
        for neighbour in neighbour_tiles:
            content = expanded_state[neighbour]
            if content is GUARD or content is KING:
                threats += 1
        if threats >= 2:
            count_threatened_tiles += 1

    guard_positions = get_live_guards_enumeration(state)
    for guard in guard_positions:
        threats = 0
        used_positions = []
        guard_neighbours = get_orthogonal_tiles_around(guard[1])
        # Examine all direct neighbour of this guard.
        for neighbour in guard_neighbours:
            content = expanded_state[neighbour]
            if content is DRAGON:
                threats += 1
                used_positions.append(neighbour)
            elif content is KING:
                used_positions.append(neighbour)
            elif content is GUARD:
                used_positions.append(neighbour)
            # If there are at least 2 threats, we need to 
            # consider if a third dragon could move into the spot on the
            # next turn.  If there are fewer than 2 dragons, there is no
            # way this guard could be captured in the next turn, so move
            # on to the next guard.
            if threats == 2:
                unoccuppied_neighbours = [x for x in guard_neighbours if x not in
                    used_positions] # positions in map
                for unoccuppied_tile in unnoccupied_neighbours:
                    second_neighbours = \
                            get_orthogonal_tiles_around(unoccuppied_tile)
                    second_neighbours += \
                            get_diagonal_tiles_around(unoccuppied_tile)
                    for n in second_neighbours: # n is a 2nd neighbour position
                        content = expanded_state[n]
                        # Increase the threat if there is a dragon on one
                        # of the neighbouring tiles, but only if the tile
                        # of interest is not on which has already been seen.
                        if n not in used_positions and content == DRAGON:
                            threats += 1
        if threats >= 3:
            count_threatened_tiles -= 1
    return count_threatened_tiles


def get_king_risk_level(king_pos, expanded_state):
    """
    Return a negative integer indicating the risk level of the king.
    The greater the value, the more risk for the king, and the better for 
    the dragon team.
    
    :param king_pos: A number 0-24 indicating the placement of the
        king on the board:
    :type king_pos: int
    :param expanded_state: The expanded state representation.
    :type expanded_state: dict(int, char)
    :return: A negative integer indicating the level of risk for the king.
    :rtype: int
    """
    surrounding_tiles = get_eight_tiles(king_pos)
    num_dragons = sum(expanded_state[i] == DRAGON for i in surrounding_tiles)
    num_guards = sum(expanded_state[i] == GUARD for i in surrounding_tiles)
    return num_guards - num_dragons

if __name__ == "__main__":
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

