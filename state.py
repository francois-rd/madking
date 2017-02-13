from array import array
import copy

"""
Index of each board tile, with the default position of each piece.

5  04 09 14 19 24     . . K . .
4  03 08 13 18 23     . G G G .
3  02 07 12 17 22     . . . . .
2  01 06 11 16 21     D D D D D
1  00 05 10 15 20     . . . . .

    A  B  C  D  E


State representation of the board.

array: | K | O | O | O | O | O | O | O | O |
         0   1   2   3   4   5   6   7   8

Each element in the board array has an integer that fits in one byte.
The king (K) is always at state[0].
The remaining 8 elements have either a guard (G) or a dragon (D).
The value in the element is 0-25 for a guard, 0-24 is the position (tile
index), and 25 means "is dead".
The value in the element is 25 or 100-124 for a dragon, 100-124 is the
position + 100 (tile index + DRAGON_BASE), and 25 means "is dead".
The first 5 bits of state[0] contain an integer 0-24, which is the position
(tile index) of the king.
Then, the remaining 3 bits in state[0] are:
- Who's turn?
    Player 1 (King) if bit 6 in state[0] == 1 (because 1 % 2 == 1)
    Player 2 (Dragon) if bit 6 in state[0] == 0 (because 0 % 2 == 0)
- Is this a winning state?
    True if bit 7 in state[0] == 1
    False if bit 7 in state[0] == 0
- Who has won this state? (assuming bit 7 in state[0] == 1)
    Player 1 (King) if bit 8 in state[0] == 1 (because 1 % 2 == 1)
    Player 2 (Dragon) if bit 8 in state[0] == 0 (because 0 % 2 == 0)
"""

KING_PLAYER = 1
DRAGON_PLAYER = 2
BOARD_NUM_RANKS = BOARD_NUM_FILES = 5
STATE_SIZE = 9
DRAGON_INITIAL_START_INDEX = 4
DEAD = 25
DRAGON_BASE = 100
NUM_META_STATE_BITS = 3
TURN_MASK = 0b00000100
WIN_MASK = 0b00000010
WHO_WON_MASK = 0b00000001
TOGGLE_TURN_MASK = 0b00000100
ALL_META_STATE_MASK = TURN_MASK | WIN_MASK | WHO_WON_MASK
KING = 'K'
GUARD = 'G'
DRAGON = 'D'
EMPTY = '.'
OFF_THE_BOARD = ' '
KING_WIN = 1
DRAGON_WIN = -1
DRAW = 0

DEFAULT_KING_PLUS_META_STATE_BYTE = 0b01110000
DEFAULT_INITIAL_STATE = array('B', [DEFAULT_KING_PLUS_META_STATE_BYTE,
                                    8, 13, 18, 1 + DRAGON_BASE,
                                    6 + DRAGON_BASE, 11 + DRAGON_BASE,
                                    16 + DRAGON_BASE, 21 + DRAGON_BASE])

_ord_a = ord('A')
_ord_1 = ord('1')


def get_default_game_start():
    """
    Returns the default initial game state.

    :return: default initial state
    """
    return copy.deepcopy(DEFAULT_INITIAL_STATE)


def create_state_from(who_s_turn, initial_positions):
    """
    Given a player's turn, and a list of STATE_SIZE numbers representing board
    positions, creates and returns a state representing the given positions,
    and with the correct player's turn.

    Assumes 'who_s_turn' is either KING_PLAYER or DRAGON_PLAYER, and assumes
    'initial_positions' is a list of STATE_SIZE numbers either between 0-24
    (for guard or king positions) or 100-124 (for dragon positions), or 25 for
    something dead (either guard or dragon).

    :param who_s_turn: player turn; either KING_PLAYER or DRAGON_PLAYER
    :type who_s_turn: byte
    :param initial_positions: STATE_SIZE numbers representing board positions
    :type initial_positions: list(byte)
    :return: a state representing the given positions with the correct turn
    :rtype: array of bytes
    """
    base_num = initial_positions[0]
    initial_positions[0] = ((base_num << 1) | (who_s_turn % 2)) << 2
    return array('B', initial_positions)


def create_expanded_state_representation(state):
    """
    Given a compact state array, returns a dict where the keys are the board
    tile indices (0-24), and the values are characters representing the type of
    piece in that tile (of one KING, GUARD, DRAGON, or EMPTY).

    :param state: a compact state representation
    :type state: array of bytes
    :return: an expanded state representation
    :rtype: dict(byte, char)
    """
    representation = {i: '.' for i in range(BOARD_NUM_RANKS * BOARD_NUM_FILES)}
    representation[get_king_tile_index(state)] = 'K'
    for i in range(1, STATE_SIZE):
        num = state[i]
        is_living_dragon = num >= DRAGON_BASE
        if is_living_dragon:
            num -= DRAGON_BASE
        if num != DEAD:
            representation[num] = 'D' if is_living_dragon else 'G'
    return representation


def get_live_pieces_enumeration_no_king(state):
    """
    Returns a list of (<index-into-the-given-state-array>,
    <byte-value-at-that-index>) pairs (which is known as an enumeration) for
    all pieces that are still alive in the given state, except the king, who is
    always deemed alive (even if DRAGON_PLAYER won, the game ends when the king
    is just about to get captured). The byte value is the raw byte value, so in
    particular, this value is the correct tile index for guards, is the tile
    index + DRAGON_BASE for dragons, and is never the byte value for DEAD, as
    these are filtered out.

    :param state: a compact state representation
    :type state: array of bytes
    :return: a list of (<index-into-the-given-state-array>,
        <byte-value-at-that-index>) for all alive pieces that are not the king
    :rtype: list((int, byte)
    """
    return [(i, val) for i, val in enumerate(state) if i > 0 and val != DEAD]


def get_live_guards_enumeration(state):
    """
    Returns a list of (<index-into-the-given-state-array>,
    <byte-value-at-that-index>) pairs (which is known as an enumeration) for
    all guards that are still alive in the given state. The byte value is the
    raw byte value, so in particular, this value is the correct tile index for
    guards, and is never the byte value for DEAD, as these guards are filtered
    out.

    :param state: a compact state representation
    :type state: array of bytes
    :return: a list of (<index-into-the-given-state-array>,
        <byte-value-at-that-index>) for all alive guards
    :rtype: list((int, byte)
    """
    return [(i, val) for i, val in enumerate(state) if i > 0 and val < DEAD]


def get_live_dragon_enumeration(state):
    """
    Returns a list of (<index-into-the-given-state-array>,
    <byte-value-at-that-index>) pairs (which is known as an enumeration) for
    all dragons that are still alive in the given state. The byte value is the
    raw byte value, so in particular, this value is tile index + DRAGON_BASE
    for dragons, and is never the byte value for DEAD, as these dragons are
    filtered out.

    :param state: a compact state representation
    :type state: array of bytes
    :return: a list of (<index-into-the-given-state-array>,
        <byte-value-at-that-index>) for all alive dragons
    :rtype: list((int, byte)
    """
    return [(i, val) for i, val in enumerate(state) if i > 0 and val > DEAD]


def tile_index(str_pos):
    """
    Returns the tile index corresponding to the given position (range is 0-24).

    :param str_pos: position of the piece represented as 'A1', 'A2', ..., 'E5'
    :type str_pos: string
    :return: the tile index corresponding to the given position (range is 0-24)
    :rtype: byte
    """
    return (ord(str_pos[0]) - _ord_a) * BOARD_NUM_RANKS + ord(
        str_pos[1]) - _ord_1


def string_position(tile_idx):
    """
    Returns the position of the piece represented as 'A1', 'A2', ..., 'E5'.

    :param tile_idx: position of the piece as in number from 0 to 24
    :type tile_idx: byte
    :return: the position of the piece represented as 'A1', 'A2', ..., 'E5'
    :rtype: string
    """
    return chr((tile_idx // BOARD_NUM_RANKS) + _ord_a) + chr(
        (tile_idx % BOARD_NUM_RANKS) + _ord_1)


def get_king_tile_index(state):
    """
    Returns the tile index (0-24) corresponding to the position of the king.

    :param state: a compact state representation
    :type state: array of bytes
    :return: the tile index (0-24) corresponding to the position of the king
    :rtype: byte
    """
    return int(state[0]) >> NUM_META_STATE_BITS


def set_king_tile_index(state, tile_idx):
    """
    Sets the king's tile index to the given index. Assumes the range is valid
    (i.e. is 0-24).

    :param state: a compact state representation
    :type state: array of bytes
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    """
    state[0] = (tile_idx << NUM_META_STATE_BITS) | (
        int(state[0]) & ALL_META_STATE_MASK)


def player_turn(state):
    """
    Returns which player's turn it is in the given state.

    :param state: a compact state representation
    :type state: array of bytes
    :return: one of KING_PLAYER or DRAGON_PLAYER
    :rtype: byte
    """
    if (int(state[0]) & TURN_MASK) == 0:
        return DRAGON_PLAYER
    else:
        return KING_PLAYER


def _change_player_turn(state):
    """
    Changes the player's turn. If it's the king player's turn, then turn is
    changed to the dragon player's turn. If it's the dragon player's turn, then
    turn is changed to the king player's turn.

    :param state: a compact state representation
    :type state: array of bytes
    """
    state[0] ^= TOGGLE_TURN_MASK


def is_winning_state(state):
    """
    Returns True if the winning state byte of the given state is set to 1, and
    False otherwise. *** Does NOT compute whether the given state represents a
    win for either player. ***

    :param state: a compact state representation
    :type state: array of bytes
    :return: True iff the winning state byte of the given state is set to 1
    :rtype: bool
    """
    return (int(state[0]) & WIN_MASK) != 0


def who_won(state):
    """
    Returns which player won ASSUMING that is_winning_state() returns True.
    *** Does NOT check this precondition for the sake of efficiency. ***

    :param state: a compact state representation
    :type state: array of bytes
    :return: one of KING_PLAYER or DRAGON_PLAYER
    :rtype: byte
    """
    if (int(state[0]) & WHO_WON_MASK) == 0:
        return DRAGON_PLAYER
    else:
        return KING_PLAYER


def check_left(expanded_state, tile_idx, tile_contents=None):
    """
    Returns (<is-left-tile-on-the-board>,
             <is-left-tile-piece-in-tile-contents>,
             <tile-index-of-left-tile>,
             <what-is-at-the-left-tile>),
        where
            <is-left-tile-on-the-board> is True iff the tile to the left of
                the given tile is on the board,
            <is-left-tile-piece-in-tile-contents> is True iff the piece on the
                tile to the left of the given tile is one of the pieces listed
                in 'tile_contents',
            <tile-index-of-left-tile> is the tile index of the tile to the left
                of the given tile, and
            <what-is-at-the-left-tile> contains the character representation of
                the piece on the tile to the left of the given tile (one of
                KING, GUARD, DRAGON, or EMPTY), or OFF_THE_BOARD if the left
                tile is off the board.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :param tile_contents: a list of the character representation of the pieces
        that may be on the tile to the left of the given tile; if None,
        <is-left-tile-piece-in-tile-contents> will be False, but
        <tile-index-of-left-tile> and <what-is-at-the-left-tile> will still be
        correct; default is None
    :type tile_contents: list(char)
    :return: (<is-left-tile-on-the-board>,
             <is-left-tile-piece-in-tile-contents>,
             <tile-index-of-left-tile>,
             <what-is-at-the-left-tile>)
    :rtype: (bool, bool, byte, char)
    """
    idx_to_left = tile_idx - BOARD_NUM_RANKS
    if idx_to_left >= 0:
        at_left = expanded_state[idx_to_left]
        if tile_contents is not None and at_left in tile_contents:
            return True, True, idx_to_left, at_left
        else:
            return True, False, idx_to_left, at_left
    else:
        return False, False, idx_to_left, OFF_THE_BOARD


def check_right(expanded_state, tile_idx, tile_contents=None):
    """
    Returns (<is-right-tile-on-the-board>,
             <is-right-tile-piece-in-tile-contents>,
             <tile-index-of-right-tile>,
             <what-is-at-the-right-tile>),
        where
            <is-right-tile-on-the-board> is True iff the tile to the right of
                the given tile is on the board,
            <is-right-tile-piece-in-tile-contents> is True iff the piece on the
                tile to the right of the given tile is one of the pieces listed
                in 'tile_contents',
            <tile-index-of-right-tile> is the tile index of the tile to the
                right of the given tile, and
            <what-is-at-the-right-tile> contains the character representation
                of the piece on the tile to the right of the given tile (one of
                KING, GUARD, DRAGON, or EMPTY), or OFF_THE_BOARD if the right
                tile is off the board.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :param tile_contents: a list of the character representation of the pieces
        that may be on the tile to the right of the given tile; if None,
        <is-right-tile-piece-in-tile-contents> will be False, but
        <tile-index-of-right-tile> and <what-is-at-the-right-tile> will still
        be correct; default is None
    :type tile_contents: list(char)
    :return: (<is-right-tile-on-the-board>,
             <is-right-tile-piece-in-tile-contents>,
             <tile-index-of-right-tile>,
             <what-is-at-the-right-tile>)
    :rtype: (bool, bool, byte, char)
    """
    idx_to_right = tile_idx + BOARD_NUM_RANKS
    if idx_to_right < BOARD_NUM_RANKS * BOARD_NUM_FILES:
        at_right = expanded_state[idx_to_right]
        if tile_contents is not None and at_right in tile_contents:
            return True, True, idx_to_right, at_right
        else:
            return True, False, idx_to_right, at_right
    else:
        return False, False, idx_to_right, OFF_THE_BOARD


def check_above(expanded_state, tile_idx, tile_contents=None):
    """
    Returns (<is-above-tile-on-the-board>,
             <is-above-tile-piece-in-tile-contents>,
             <tile-index-of-above-tile>,
             <what-is-at-the-above-tile>),
        where
            <is-above-tile-on-the-board> is True iff the tile above the given
            tile is on the board,
            <is-above-tile-piece-in-tile-contents> is True iff the piece on the
                tile above the given tile is one of the pieces listed in
                'tile_contents',
            <tile-index-of-above-tile> is the tile index of the tile above the
                given tile, and
            <what-is-at-the-above-tile> contains the character representation
                of the piece on the tile above the given tile (one of KING,
                GUARD, DRAGON, or EMPTY), or OFF_THE_BOARD if the above
                tile is off the board.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :param tile_contents: a list of the character representation of the pieces
        that may be on the tile above the given tile; if None,
        <is-above-tile-piece-in-tile-contents> will be False, but
        <tile-index-of-above-tile> and <what-is-at-the-above-tile> will still
        be correct; default is None
    :type tile_contents: list(char)
    :return: (<is-above-tile-on-the-board>,
             <is-above-tile-piece-in-tile-contents>,
             <tile-index-of-above-tile>,
             <what-is-at-the-above-tile>)
    :rtype: (bool, bool, byte, char)
    """
    idx_above = tile_idx + 1
    if idx_above % BOARD_NUM_RANKS != 0:
        above = expanded_state[idx_above]
        if tile_contents is not None and above in tile_contents:
            return True, True, idx_above, above
        else:
            return True, False, idx_above, above
    else:
        return False, False, idx_above, OFF_THE_BOARD


def check_below(expanded_state, tile_idx, tile_contents=None):
    """
    Returns (<is-below-tile-on-the-board>,
             <is-below-tile-piece-in-tile-contents>,
             <tile-index-of-below-tile>,
             <what-is-at-the-below-tile>),
        where
            <is-below-tile-on-the-board> is True iff the tile below the given
            tile is on the board,
            <is-below-tile-piece-in-tile-contents> is True iff the piece on the
                tile below the given tile is one of the pieces listed in
                'tile_contents',
            <tile-index-of-below-tile> is the tile index of the tile below the
                given tile, and
            <what-is-at-the-below-tile> contains the character representation
                of the piece on the tile below the given tile (one of KING,
                GUARD, DRAGON, or EMPTY), or OFF_THE_BOARD if the below
                tile is off the board.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: the tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :param tile_contents: a list of the character representation of the pieces
        that may be on the tile below the given tile; if None,
        <is-below-tile-piece-in-tile-contents> will be False, but
        <tile-index-of-below-tile> and <what-is-at-the-below-tile> will still
        be correct; default is None
    :type tile_contents: list(char)
    :return: (<is-below-tile-on-the-board>,
             <is-below-tile-piece-in-tile-contents>,
             <tile-index-of-below-tile>,
             <what-is-at-the-below-tile>)
    :rtype: (bool, bool, byte, char)
    """
    idx_below = tile_idx - 1
    if tile_idx % BOARD_NUM_RANKS != 0:
        below = expanded_state[idx_below]
        if tile_contents is not None and below in tile_contents:
            return True, True, idx_below, below
        else:
            return True, False, idx_below, below
    else:
        return False, False, idx_below, OFF_THE_BOARD


# TODO: no yet implemented! Don't use!
def is_king_captured(expanded_state, king_tile_index):
    _, dragon_left, left_idx, at_left = check_left(expanded_state,
                                                   king_tile_index, [DRAGON])
    _, dragon_right, right_idx, at_right = check_right(expanded_state,
                                                       king_tile_index,
                                                       [DRAGON])
    _, dragon_above, above_idx, at_above = check_above(expanded_state,
                                                       king_tile_index,
                                                       [DRAGON])
    _, dragon_below, below_idx, at_below = check_below(expanded_state,
                                                       king_tile_index,
                                                       [DRAGON])
    # TODO: does it matter if it's the king player's turn or not? Yes!
    if dragon_left and dragon_above and dragon_right:
        some_dragon_can_be_captured = \
            is_dragon_surrounded(expanded_state, left_idx) or \
            is_dragon_surrounded(expanded_state, above_idx) or \
            is_dragon_surrounded(expanded_state, right_idx)
        if dragon_below:
            # TODO: what if any of these dragons can get captured by a guard?
            # Then, the king could escape by jumping over the guard that moves
            # into the tile where the dragon was, so long as the tile beyond
            # the jumped-over guard is free. But this would take an extra turn.
            # The game rules aren't clear about what happens in this case, i.e.
            # because the king COULD escape by moving (on the next turn), he
            # isn't truly caught.... this would be weird though!
            return True
        elif at_below == EMPTY:
            # TODO: what if the tile below is ALSO surrounded by 3 dragons
            # (e.g. if there are 6 dragons because one guard got captured)?
            # Again, the rules aren't clear.
            return False
        elif at_below == OFF_THE_BOARD:
            # Check if any of the dragons can be captured by a guard.
            # This only applies if it's the king's turn.
            return not some_dragon_can_be_captured
        else:  # Must be a guard below.
            if some_dragon_can_be_captured:
                return False
            else:
                _, _, _, double_below = check_below(expanded_state, below_idx)
                return double_below != EMPTY  # King can jump over guard below.
    # TODO: the other three possible ways 3 dragons can surround the king.
    pass


def is_guard_surrounded(expanded_state, guard_idx):
    """
    Returns True iff the guard at the given tile index is surrounded by at
    least 3 dragons. *** Does NOT verify that the given tile actually contains
    a guard, for efficiency reasons. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param guard_idx: the tile index (0-24) corresponding to a board position
    :type guard_idx: byte
    :return: True iff 3 dragons surround the guard at the given tile index
    :rtype: bool
    """
    _, dragon_left, _, _ = check_left(expanded_state, guard_idx, [DRAGON])
    _, dragon_right, _, _ = check_right(expanded_state, guard_idx, [DRAGON])
    _, dragon_above, _, _ = check_above(expanded_state, guard_idx, [DRAGON])
    _, dragon_below, _, _ = check_below(expanded_state, guard_idx, [DRAGON])
    return (dragon_left and dragon_above and dragon_right) or \
           (dragon_above and dragon_right and dragon_below) or \
           (dragon_right and dragon_below and dragon_left) or \
           (dragon_below and dragon_left and dragon_above)


def is_dragon_surrounded(expanded_state, dragon_idx):
    """
    Returns True iff the dragon at the given tile index is surrounded by at
    least 2 guards. *** Does NOT verify that the given tile actually contains
    a dragon, for efficiency reasons. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param dragon_idx: the tile index (0-24) corresponding to a board position
    :type dragon_idx: byte
    :return: True iff 2 guards surround dragon at the given tile index
    :rtype: bool
    """
    _, guard_left, _, _ = check_left(expanded_state, dragon_idx, [GUARD])
    _, guard_right, _, _ = check_right(expanded_state, dragon_idx, [GUARD])
    _, guard_above, _, _ = check_above(expanded_state, dragon_idx, [GUARD])
    _, guard_below, _, _ = check_below(expanded_state, dragon_idx, [GUARD])
    return (guard_left and guard_above) or \
           (guard_above and guard_right) or \
           (guard_right and guard_below) or \
           (guard_below and guard_left) or \
           (guard_left and guard_right) or \
           (guard_above and guard_below)


def move(state, expanded_state, from_tile_idx, to_tile_idx):
    """
    Modifies the given state to reflect a move of a piece on the board. If it's
    a guard moving, and the guard is moving onto a tile containing a dragon,
    the corresponding dragon is set to DEAD (assumed to be captured). If it's a
    guard moving, and the guard moves onto a tile surrounded by at least 3
    dragons, the guard is converted to a dragon. If it's a dragon moving, and
    the dragon moves onto a tile such that this move results in one or more
    guards begin surrounded by at least 3 dragons, all guards that become
    surrounded are converted to dragons. This includes guards captured by
    propagation (one guard is converted to a dragon, which causes another guard
    to be surrounded by at least 3 dragons due to the position of the newly-
    converted dragon).

    After the move is performed, the player's turn is changed.

    *** Assumes the move is valid. Does NOT check if the
    resulting condition is terminal (i.e. a win for one player, or a draw for
    both). ***

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param from_tile_idx: tile index (0-24) corresponding to a board position
    :type from_tile_idx: byte
    :param to_tile_idx: tile index (0-24) corresponding to a board position
    :type to_tile_idx: byte
    """
    if get_king_tile_index(state) == from_tile_idx:
        set_king_tile_index(state, to_tile_idx)
        expanded_state[from_tile_idx] = EMPTY
        expanded_state[to_tile_idx] = KING
    else:
        living = get_live_pieces_enumeration_no_king(state)  # Inline this?
        for i, idx_i in living:
            if idx_i % DRAGON_BASE == from_tile_idx:
                if idx_i == from_tile_idx:  # If it's a guard.
                    # Maybe the guard moved onto a dragon?
                    for j, idx_j in living:
                        if idx_j == to_tile_idx + DRAGON_BASE:
                            state[j] = DEAD  # If so, capture the dragon.
                            break
                    # Either way, move the guard.
                    state[i] = to_tile_idx
                    expanded_state[from_tile_idx] = EMPTY
                    expanded_state[to_tile_idx] = GUARD
                    # We'll check for a dragon 3-surround later.
                    break
                else:  # If it's not a G, but it's a G or a D, it must be a D.
                    # Just move the dragon. We'll check for a 3-surround later.
                    state[i] = to_tile_idx + DRAGON_BASE
                    expanded_state[from_tile_idx] = EMPTY
                    expanded_state[to_tile_idx] = DRAGON
                    break
    # For any guard that it now in a dragon 3-surround, convert it to a dragon.
    # Then, check again to see if the conversion causes a chain reaction.
    while True:
        converted_a_guard = False
        for i, guard_idx in get_live_guards_enumeration(state):
            if is_guard_surrounded(expanded_state, guard_idx):
                state[i] += DRAGON_BASE
                expanded_state[guard_idx] = DRAGON
                converted_a_guard = True
                break
        if not converted_a_guard:
            break
    # After the move, we toggle the player's turn.
    _change_player_turn(state)


def _all_orthogonal_moves(expanded_state, tile_idx):
    """
    Returns a dictionary where the keys are 'l', 'r', 'a', and 'b', and the
    values are the tuple returned by check_left(), check_right(),
    check_above(), and check_below(), respectively. *** Assumes the given tile
    index is between 0-24, and that there is a piece on that tile, and that
    it's the correct player's turn. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a dictionary where the keys are 'l', 'r', 'a', and 'b', and the
        values are the tuple returned by check_left(), check_right(),
        check_above(), and check_below(), respectively
    :rtype: dict(char, (bool, bool, byte, char))
    """
    return {
        'l': check_left(expanded_state, tile_idx, [EMPTY]),
        'r': check_right(expanded_state, tile_idx, [EMPTY]),
        'a': check_above(expanded_state, tile_idx, [EMPTY]),
        'b': check_below(expanded_state, tile_idx, [EMPTY])
    }


def _all_valid_moves_for_king(expanded_state, king_tile_index):
    """
    Returns a list of (from_tile_idx, to_tile_idx) pairs representing all the
    valid moves that the king can make. *** Assumes the given tile index is
    between 0-24, and that the king is actually on that tile, and that it's the
    king player's turn. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_index: tile index (0-24) corresponding to a board position
    :type king_tile_index: byte
    :return: a list of (from_tile_idx, to_tile_idx) pairs representing all the
        valid moves the king can make
    :rtype: list((byte, byte))
    """
    moves = _all_orthogonal_moves(expanded_state, king_tile_index)
    # Moves doesn't contain possible jumps over guards. So, for each move, if
    # the move would land on a guard, replace it with a move that may jump over
    # the guard, if applicable.
    _, _, left_idx, at_left = moves['l']
    if at_left == GUARD:
        # King can't both move left and jump over on left, so just replace.
        moves['l'] = check_left(expanded_state, left_idx, [EMPTY])
    _, _, right_idx, at_right = moves['r']
    if at_right == GUARD:
        # King can't both move right and jump over on right, so just replace.
        moves['r'] = check_right(expanded_state, right_idx, [EMPTY])
    _, _, above_idx, at_above = moves['a']
    if at_above == GUARD:
        # King can't both move up and jump over upwards, so just replace.
        moves['a'] = check_above(expanded_state, above_idx, [EMPTY])
    _, _, below_idx, at_below = moves['b']
    if at_below == GUARD:
        # King can't both move down and jump over downwards, so just replace.
        moves['b'] = check_below(expanded_state, below_idx, [EMPTY])
    return [(king_tile_index, tile_idx) for _, _, tile_idx, at_tile in
            moves.values() if at_tile == EMPTY]


def _all_valid_moves_for_guard(expanded_state, tile_idx):
    """
    Returns a list of (from_tile_idx, to_tile_idx) pairs representing all the
    valid moves that the guard at the given tile index can make. *** Assumes
    the given tile index is between 0-24, and that a guard is actually on that
    tile, and that it's the king player's turn. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of (from_tile_idx, to_tile_idx) pairs representing all the
        valid moves the guard at the given tile index can make
    :rtype: list((byte, byte))
    """
    moves = _all_orthogonal_moves(expanded_state, tile_idx)
    # Moves doesn't contain possible dragon captures. So, for each move, if the
    # move would land on a dragon, check the tiles surrounding the dragon to
    # see if there is another guard. If so, one possible move is to capture the
    # dragon.
    _, _, left_idx, at_left = moves['l']
    if at_left == DRAGON and is_dragon_surrounded(expanded_state, left_idx):
        moves['l'] = (True, True, left_idx, at_left)
    _, _, right_idx, at_right = moves['r']
    if at_right == DRAGON and is_dragon_surrounded(expanded_state, right_idx):
        moves['r'] = (True, True, right_idx, at_right)
    _, _, above_idx, at_above = moves['a']
    if at_above == DRAGON and is_dragon_surrounded(expanded_state, above_idx):
        moves['a'] = (True, True, above_idx, at_above)
    _, _, below_idx, at_below = moves['b']
    if at_below == DRAGON and is_dragon_surrounded(expanded_state, below_idx):
        moves['b'] = (True, True, below_idx, at_below)
    return [(tile_idx, to_tile_idx) for _, is_valid, to_tile_idx, _ in
            moves.values() if is_valid]


def _all_valid_moves_for_dragon(expanded_state, tile_idx):
    """
    Returns a list of (from_tile_idx, to_tile_idx) pairs representing all the
    valid moves that the dragon at the given tile index can make. *** Assumes
    the given tile index is between 0-24, and that a dragon is actually on that
    tile, and that it's the dragon player's turn. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of (from_tile_idx, to_tile_idx) pairs representing all the
        valid moves the dragon at the given tile index can make
    :rtype: list((byte, byte))
    """
    moves = _all_orthogonal_moves(expanded_state, tile_idx)
    # Moves doesn't contain possible diagonal moves, so check those and add
    # them in if applicable.
    on_board, _, left_idx, _ = moves['l']
    if on_board:
        moves['al'] = check_above(expanded_state, left_idx, [EMPTY])
        moves['bl'] = check_below(expanded_state, left_idx, [EMPTY])
    on_board, _, right_idx, _ = moves['r']
    if on_board:
        moves['ar'] = check_above(expanded_state, right_idx, [EMPTY])
        moves['br'] = check_below(expanded_state, right_idx, [EMPTY])
    return [(tile_idx, to_tile_idx) for _, is_empty, to_tile_idx, _ in
            moves.values() if is_empty]


def all_valid_moves(state, expanded_state):
    """
    Returns a list of (from_tile_idx, to_tile_idx) pairs representing all the
    valid moves that every piece that is alive can make in the given state,
    depending on which player's turn it is.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a list of (from_tile_idx, to_tile_idx) pairs representing all the
        valid moves that every piece that is alive can make in the given state,
        depending on which player's turn it is
    :rtype: list((byte, byte))
    """
    all_moves = []
    if player_turn(state) == KING_PLAYER:
        all_moves.extend(_all_valid_moves_for_king(expanded_state,
                                                   get_king_tile_index(state)))
        for _, idx in get_live_guards_enumeration(state):
            all_moves.extend(_all_valid_moves_for_guard(expanded_state, idx))
    else:  # It's DRAGON_PLAYER's turn.
        for _, idx in get_live_dragon_enumeration(state):
            all_moves.extend(_all_valid_moves_for_dragon(expanded_state,
                                                         idx - DRAGON_BASE))
    return all_moves


def is_terminal(state, expanded_state):
    """
    Returns a pair (<is-terminal>, <utility>). If it's a draw, then
    returns (True, DRAW). If it's a win for the king player, then returns
    (True, KING_WIN). If it's a win for the dragon player, then returns
    (True, DRAGON_WIN). Otherwise, returns (False, 0).

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a pair (<is-terminal>, <utility>)
    :rtype: (bool, int)
    """

    if len(get_live_dragon_enumeration(state)) == 0:
        return True, KING_WIN
    king_tile_index = get_king_tile_index(state)
    if king_tile_index % 5 == 0:
        return True, KING_WIN
    if len(_all_valid_moves_for_king(expanded_state, king_tile_index)) == 0:
        if king_tile_index in [0, BOARD_NUM_RANKS - 1,
                               (BOARD_NUM_RANKS * BOARD_NUM_FILES) - 1,
                               BOARD_NUM_RANKS * (BOARD_NUM_FILES - 1)]:
            return True, DRAW
        else:
            return True, DRAGON_WIN
    return False, 0


def is_valid_move(state, expanded_state, from_tile_idx, to_tile_idx):
    """
    Returns True iff moving the piece on the 'from_tile_idx' tile to the
    'to_file_idx' tile is a valid move, given who's turn it is. *** Assumes the
    given tile indices are valid (i.e. have range 0 to 24). ***

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param from_tile_idx: tile index (0-24) corresponding to a board position
    :type from_tile_idx: byte
    :param to_tile_idx: tile index (0-24) corresponding to a board position
    :type to_tile_idx: byte
    :return: True iff the move is valid
    :rtype: bool
    """
    at_from_tile = expanded_state[from_tile_idx]
    if at_from_tile == EMPTY:
        return False

    if player_turn(state) == KING_PLAYER:
        if at_from_tile == KING:
            return (from_tile_idx, to_tile_idx) in \
                   _all_valid_moves_for_king(expanded_state, from_tile_idx)
        elif at_from_tile == GUARD:
            return (from_tile_idx, to_tile_idx) in \
                   _all_valid_moves_for_guard(expanded_state, from_tile_idx)
        else:  # Because the tile contains a dragon.
            return False
    else:  # It's DRAGON_PLAYER's turn.
        if at_from_tile == DRAGON:
            return (from_tile_idx, to_tile_idx) in \
                   _all_valid_moves_for_dragon(expanded_state, from_tile_idx)
        else:  # Because the tile contains a king or a guard.
            return False


def successors(state, expanded_state):
    """
    Returns a list of (successor_state, successor_expanded_state, move) tuples,
    one tuple for each successor of the given state, where 'move' is itself a
    pair of (<from-tile-index>, <to-tile-index>).

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a list of (successor_state, successor_expanded_state, move)
        tuples, one pair for each successor of the given state
    :rtype: list((array of bytes, dict(byte, char), (byte, byte)))
    """
    all_successors = []
    for from_tile_idx, to_tile_idx in all_valid_moves(state, expanded_state):
        new_state = copy.deepcopy(state)
        new_expanded_state = create_expanded_state_representation(new_state)
        move(new_state, new_expanded_state, from_tile_idx, to_tile_idx)
        all_successors.append((new_state, new_expanded_state,
                               (from_tile_idx, to_tile_idx)))
    return all_successors


def hash_state(state):
    """
    Returns a hash string of the given state.

    :param state: a compact state representation
    :type state: array of bytes
    :return: a hash string of the given state
    :rtype: string
    """
    return ''.join(str(b) for b in state)
