from array import array
import sys
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
    Player 2 (Dragon) if bit 6 in state[0] == 0 (because 2 % 2 == 0)
- Is this a winning state?
    True if bit 7 in state[0] == 1
    False if bit 7 in state[0] == 0
- Who has won this state? (assuming bit 7 in state[0] == 1)
    Player 1 (King) if bit 8 in state[0] == 1 (because 1 % 2 == 1)
    Player 2 (Dragon) if bit 8 in state[0] == 0 (because 2 % 2 == 0)
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
ALL_META_STATE_MASK = TURN_MASK | WIN_MASK | WHO_WON_MASK
INDEX_AND_TURN_MASK = 0b11111100
KING = 'K'
GUARD = 'G'
DRAGON = 'D'
EMPTY = '.'
OFF_THE_BOARD = ' '
KING_WIN = sys.maxsize - 1
DRAGON_WIN = -sys.maxsize + 1
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


def _set_king_tile_index(state, tile_idx):
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
    state[0] ^= TURN_MASK


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


def _mark_as_winning_state(state):
    """
    Marks the given state as a winning state.

    :param state: a compact state representation
    :type state: array of bytes
    """
    state[0] |= WIN_MASK


def who_won(state):
    """
    Returns which player won assuming that is_winning_state() returns True.
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


def _set_winner(state, winning_player):
    """
    Marks the given state as being won by the given player. Assumes that
    is_winning_state() returns True. *** Does NOT check this precondition for
    the sake of efficiency. ***

    :param state: a compact state representation
    :type state: array of bytes
    :param winning_player: one of KING_PLAYER or DRAGON_PLAYER
    :type winning_player: byte
    """
    state[0] ^= (-(winning_player % 2) ^ int(state[0])) & WHO_WON_MASK


def _check_left(expanded_state, tile_idx, tile_contents=None):
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


def _check_right(expanded_state, tile_idx, tile_contents=None):
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


def _check_above(expanded_state, tile_idx, tile_contents=None):
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


def _check_below(expanded_state, tile_idx, tile_contents=None):
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


def _is_king_captured_fourth_side(state, expanded_state, king_tile_idx,
                                  first_dragon_idx, second_dragon_idx,
                                  third_dragon_idx, unknown_content_idx,
                                  unknown_content_on_board):
    """
    Given a tile with the king, and three other sides known to have dragons,
    determines whether the king is captured or not based on the unknown
    contents of the fourth side and on which player's turn it is.

    Returns (<is-king-captured>, <is-king-player's-turn>, <forced-moves>),
    where
        <is-king-captured> is True iff the king is captured and cannot possibly
            escape,
        <is-king-player's-turn> is True iff it is the king player's turn, and
        <forced-moves> is a list of (<from-tile-index>, <to-tile-index>)
            representing any of the possible moves that the king player must
            immediately make in order to avoid capture by the dragons (moves
            that are forced in order to prevent defeat). Note: if
            <is-king-captured> is True, <forced-moves> will be None because
            there are no longer any moves the king player can make to avoid
            capture. On the other hand, if <is-king-player's-turn> is False,
            then <forced-moves> will be None because it is not the king
            player's turn to move. Finally, if <is-king-captured> is False and
            <is-king-player's-turn> is True, then <forced-moves> is None iff
            the king is not in immediate enough danger that the king player
            faces a set of forced moves (so all possible legal moves are
            playable).

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_idx: tile index (0-24) corresponding to the board
        position with the king
    :type king_tile_idx: byte
    :param first_dragon_idx: tile index (0-24) corresponding to a board
        position with one of the dragons surrounding the king
    :type first_dragon_idx: byte
    :param second_dragon_idx: tile index (0-24) corresponding to a board
        position with one of the dragons surrounding the king
    :type second_dragon_idx: byte
    :param third_dragon_idx: tile index (0-24) corresponding to a board
        position with one of the dragons surrounding the king
    :type third_dragon_idx: byte
    :param unknown_content_idx: tile index (0-24) corresponding to the fourth
        board position around the king (whose content is unknown)
    :type unknown_content_idx: byte
    :param unknown_content_on_board: True iff 'unknown_content_idx' is on the
        board; even if the content of 'unknown_content_idx' is unknown, it
        should at least be known if the given index represents a tile that
        actually is on the board
    :type unknown_content_on_board: bool
    :return: (<is-king-captured>, <is-king-player's-turn>, <forced-moves>)
    :rtype: (bool, bool, list((byte, byte)))
    """
    if unknown_content_on_board:
        at_fourth_side = expanded_state[unknown_content_idx]
    else:
        at_fourth_side = OFF_THE_BOARD
    if player_turn(state) == DRAGON_PLAYER:
        return at_fourth_side != EMPTY, False, None
    else:  # It's the king player's turn.
        if at_fourth_side == EMPTY:
            return False, True, None
        elif at_fourth_side == GUARD or at_fourth_side == OFF_THE_BOARD:
            # King escapes by capturing or having a guard capture a dragon so
            # that there are just 2 dragons surrounding him. These are all
            # forced moves because if no dragon is captured, the king is.
            # Another possibility is that, if it's a guard blocking the king,
            # the guard can actually just move out of the way, so that the
            # fourth side becomes empty.
            first_dragon_forced_moves = \
                _moves_capturing_dragon_by_king_or_guard(expanded_state,
                                                         first_dragon_idx)
            second_dragon_forced_moves = \
                _moves_capturing_dragon_by_king_or_guard(expanded_state,
                                                         second_dragon_idx)
            third_dragon_forced_moves = \
                _moves_capturing_dragon_by_king_or_guard(expanded_state,
                                                         third_dragon_idx)
            forced_moves = first_dragon_forced_moves
            forced_moves.extend(second_dragon_forced_moves)
            forced_moves.extend(third_dragon_forced_moves)
            # Now, check if it's a guard, and if the guard can move.
            if at_fourth_side == GUARD:
                forced_moves.extend(
                    _all_valid_moves_for_guard(expanded_state,
                                               unknown_content_idx))
            king_is_captured = len(forced_moves) == 0
            if king_is_captured:
                forced_moves = None
            return king_is_captured, True, forced_moves
        else:  # at_fourth_side == DRAGON. So unknown_content_idx has a dragon.
            # King escapes by capturing a dragon and moving to where the dragon
            # was. This leaves the tile he was on empty, implying that the next
            # move still has an escape for him, so he won't immediately be
            # captured. If it's the guard that captures, then the king is still
            # 4-sides surrounded, and so would be captured right away.
            forced_moves = []
            if _is_dragon_surrounded_by_king_and_guard(expanded_state,
                                                       first_dragon_idx):
                forced_moves.append((king_tile_idx, first_dragon_idx))
            if _is_dragon_surrounded_by_king_and_guard(expanded_state,
                                                       second_dragon_idx):
                forced_moves.append((king_tile_idx, second_dragon_idx))
            if _is_dragon_surrounded_by_king_and_guard(expanded_state,
                                                       third_dragon_idx):
                forced_moves.append((king_tile_idx, third_dragon_idx))
            if _is_dragon_surrounded_by_king_and_guard(expanded_state,
                                                       unknown_content_idx):
                forced_moves.append((king_tile_idx, unknown_content_idx))
            king_is_captured = len(forced_moves) == 0
            if king_is_captured:
                forced_moves = None
            return king_is_captured, True, forced_moves


def _is_king_captured(state, expanded_state, king_tile_idx):
    """
    Determines whether the king is captured or not, based on the unknown
    contents of the four tiles surrounding him, and on which player's turn it
    is.

    Returns (<is-king-captured>, <is-king-player's-turn>, <forced-moves>),
    where
        <is-king-captured> is True iff the king is captured and cannot possibly
            escape,
        <is-king-player's-turn> is True iff it is the king player's turn, and
        <forced-moves> is a list of (<from-tile-index>, <to-tile-index>)
            representing any of the possible moves that the king player must
            immediately make in order to avoid capture by the dragons (moves
            that are forced in order to prevent defeat). Note: if
            <is-king-captured> is True, <forced-moves> will be None because
            there are no longer any moves the king player can make to avoid
            capture. On the other hand, if <is-king-player's-turn> is False,
            then <forced-moves> will be None because it is not the king
            player's turn to move. Finally, if <is-king-captured> is False and
            <is-king-player's-turn> is True, then <forced-moves> is None iff
            the king is not in immediate enough danger that the king player
            faces a set of forced moves (so all possible legal moves are
            playable).

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_idx: tile index (0-24) corresponding to the board
        position with the king
    :type king_tile_idx: byte
    :return: (<is-king-captured>, <is-king-player's-turn>, <forced-moves>)
    :rtype: (bool, bool, list((byte, byte)))
    """
    on_board_left, dragon_left, left_idx, at_left = \
        _check_left(expanded_state, king_tile_idx, [DRAGON])
    on_board_right, dragon_right, right_idx, at_right = \
        _check_right(expanded_state, king_tile_idx, [DRAGON])
    on_board_above, dragon_above, above_idx, at_above = \
        _check_above(expanded_state, king_tile_idx, [DRAGON])
    on_board_below, dragon_below, below_idx, at_below = \
        _check_below(expanded_state, king_tile_idx, [DRAGON])
    if dragon_left and dragon_above and dragon_right:
        return _is_king_captured_fourth_side(state, expanded_state,
                                             king_tile_idx, left_idx,
                                             above_idx, right_idx, below_idx,
                                             on_board_below)
    elif dragon_above and dragon_right and dragon_below:
        return _is_king_captured_fourth_side(state, expanded_state,
                                             king_tile_idx, above_idx,
                                             right_idx, below_idx, left_idx,
                                             on_board_left)
    elif dragon_right and dragon_below and dragon_left:
        return _is_king_captured_fourth_side(state, expanded_state,
                                             king_tile_idx, right_idx,
                                             below_idx, left_idx, above_idx,
                                             on_board_above)
    elif dragon_below and dragon_left and dragon_above:
        return _is_king_captured_fourth_side(state, expanded_state,
                                             king_tile_idx, below_idx,
                                             left_idx, above_idx, right_idx,
                                             on_board_right)
    else:  # There aren't at least 3 dragons surrounding the king.
        return False, player_turn(state) == KING_PLAYER, None


def _is_guard_surrounded(expanded_state, guard_idx):
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
    _, dragon_left, _, _ = _check_left(expanded_state, guard_idx, [DRAGON])
    _, dragon_right, _, _ = _check_right(expanded_state, guard_idx, [DRAGON])
    _, dragon_above, _, _ = _check_above(expanded_state, guard_idx, [DRAGON])
    _, dragon_below, _, _ = _check_below(expanded_state, guard_idx, [DRAGON])
    return (dragon_left and dragon_above and dragon_right) or \
           (dragon_above and dragon_right and dragon_below) or \
           (dragon_right and dragon_below and dragon_left) or \
           (dragon_below and dragon_left and dragon_above)


def _is_king_surrounded(expanded_state, king_idx):
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
    _, dragon_left, _, _ = _check_left(expanded_state, king_idx, [DRAGON])
    _, dragon_right, _, _ = _check_right(expanded_state, king_idx, [DRAGON])
    _, dragon_above, _, _ = _check_above(expanded_state, king_idx, [DRAGON])
    _, dragon_below, _, _ = _check_below(expanded_state, king_idx, [DRAGON])
    return (dragon_left and dragon_above and dragon_right) or \
           (dragon_above and dragon_right and dragon_below) or \
           (dragon_right and dragon_below and dragon_left) or \
           (dragon_below and dragon_left and dragon_above)


def _is_dragon_surrounded_by_king_and_guard(expanded_state, dragon_idx):
    """
    Returns True iff the dragon at the given tile index is surrounded by at the
    king and at least 1 guard. *** Does NOT verify that the given tile actually
    contains a dragon, for efficiency reasons. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param dragon_idx: the tile index (0-24) corresponding to a board position
    :type dragon_idx: byte
    :return: True iff the king and 1 guard surround the dragon at the given
        tile index
    :rtype: bool
    """
    _, _, _, at_left = _check_left(expanded_state, dragon_idx, [KING])
    _, _, _, at_right = _check_right(expanded_state, dragon_idx, [KING])
    _, _, _, at_above = _check_above(expanded_state, dragon_idx, [KING])
    _, _, _, at_below = _check_below(expanded_state, dragon_idx, [KING])
    if at_left == KING:
        return at_right == GUARD or at_above == GUARD or at_below == GUARD
    elif at_right == KING:
        return at_left == GUARD or at_above == GUARD or at_below == GUARD
    elif at_above == KING:
        return at_left == GUARD or at_right == GUARD or at_below == GUARD
    elif at_below == KING:
        return at_left == GUARD or at_right == GUARD or at_above == GUARD
    else:
        return False


def _moves_capturing_dragon_by_king_or_guard(expanded_state, dragon_idx):
    """
    Returns a list of (<from-tile-index>, <to-tile-index>) pairs, each of which
    represents one possible move that the king player (if it's the king
    player's turn) could make that would result in the dragon being captured,
    or the empty list if there are no such moves. *** Does NOT verify that the
    given tile actually contains a dragon, for efficiency reasons. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param dragon_idx: the tile index (0-24) corresponding to a board position
    :type dragon_idx: byte
    :return: a list of (<from-tile-index>, <to-tile-index>) pairs representing
        moves that would capture the dragon at the given tile index
    :rtype: list((byte, byte))
    """
    _, guard_or_king_left, left_idx, _ = _check_left(expanded_state, dragon_idx,
                                                     [KING, GUARD])
    _, guard_or_king_right, right_idx, _ = _check_right(expanded_state,
                                                        dragon_idx,
                                                        [KING, GUARD])
    _, guard_or_king_above, above_idx, _ = _check_above(expanded_state,
                                                        dragon_idx,
                                                        [KING, GUARD])
    _, guard_or_king_below, below_idx, _ = _check_below(expanded_state,
                                                        dragon_idx,
                                                        [KING, GUARD])
    at_left_can_capture = at_right_can_capture = False
    at_above_can_capture = at_below_can_capture = False
    if guard_or_king_left and guard_or_king_above:
        at_left_can_capture = at_above_can_capture = True
    if guard_or_king_above and guard_or_king_right:
        at_above_can_capture = at_right_can_capture = True
    if guard_or_king_right and guard_or_king_below:
        at_right_can_capture = at_below_can_capture = True
    if guard_or_king_below and guard_or_king_left:
        at_below_can_capture = at_left_can_capture = True
    if guard_or_king_left and guard_or_king_right:
        at_left_can_capture = at_right_can_capture = True
    if guard_or_king_above and guard_or_king_below:
        at_above_can_capture = at_below_can_capture = True
    moves = []
    if at_left_can_capture:
        moves.append((left_idx, dragon_idx))
    if at_right_can_capture:
        moves.append((right_idx, dragon_idx))
    if at_above_can_capture:
        moves.append((above_idx, dragon_idx))
    if at_below_can_capture:
        moves.append((below_idx, dragon_idx))
    return moves


def _is_dragon_surrounded(expanded_state, dragon_idx):
    """
    Returns True iff the dragon at the given tile index is surrounded by at
    least 2 guards, or by the king and at least 1 guard. *** Does NOT verify
    that the given tile actually contains a dragon, for efficiency reasons. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param dragon_idx: the tile index (0-24) corresponding to a board position
    :type dragon_idx: byte
    :return: True iff at least 2 guards, or the king and at least 1 guard
        surround the dragon at the given tile index
    :rtype: bool
    """
    _, guard_or_king_left, _, _ = _check_left(expanded_state, dragon_idx,
                                              [KING, GUARD])
    _, guard_or_king_right, _, _ = _check_right(expanded_state, dragon_idx,
                                                [KING, GUARD])
    _, guard_or_king_above, _, _ = _check_above(expanded_state, dragon_idx,
                                                [KING, GUARD])
    _, guard_or_king_below, _, _ = _check_below(expanded_state, dragon_idx,
                                                [KING, GUARD])
    return (guard_or_king_left and guard_or_king_above) or \
           (guard_or_king_above and guard_or_king_right) or \
           (guard_or_king_right and guard_or_king_below) or \
           (guard_or_king_below and guard_or_king_left) or \
           (guard_or_king_left and guard_or_king_right) or \
           (guard_or_king_above and guard_or_king_below)


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


def is_dragon_threatened(state, expanded_state):
    """
    Returns the number of DRAGONS threatened to be captured by the king player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: if any of the dragon is captured
    :rtype: bool
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
    return (count_threatened_tiles > 0)


def is_guard_threatened(state, expanded_state):
    """
    Returns the number of GUARDS threatened to be captured by the dragon player.

    :param state: the current node in the search
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: if any of the guards is captured
    :rtype: bool
    """
    #TODO Double-check this function for correctness.
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
            count_threatened_tiles += 1
    return (count_threatened_tiles > 0)


def is_piece_threatened(state, expanded_state):
    return is_guard_threatened(state, expanded_state) or \
           is_dragon_threatened(state, expanded_state) or \
           _is_king_surrounded(expanded_state, get_king_tile_index(state))

def can_king_win(state, expanded_state):
    king_index = get_king_tile_index(state)
    return king_index in [1, 6 ,11, 16, 21 ] and \
           expanded_state[king_index-1] == EMPTY

def move_piece(state, expanded_state, from_tile_idx, to_tile_idx):
    """
    Modifies the given state and expanded state to reflect a move of a piece on
    the board. If it's a guard or a king moving, and the guard or king is
    moving onto a tile containing a dragon, the corresponding dragon is set to
    DEAD (assumed to be captured). If it's a guard moving, and the guard moves
    onto a tile surrounded by at least 3 dragons, the guard is converted to a
    dragon. If it's a dragon moving, and the dragon moves onto a tile such that
    this move results in one or more guards begin surrounded by at least 3
    dragons, all guards that become surrounded are converted to dragons. In
    both cases, whenever a guard is converted to a dragon, the change is
    propagated (i.e. one guard is converted to a dragon, which causes another
    guard to be surrounded by at least 3 dragons due to the position of the
    newly-converted dragon).

    After the move is performed, the player's turn is changed.

    *** Assumes the move is valid. Does NOT check if the resulting condition is
    terminal (i.e. a win for one player, or a draw for both). ***

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param from_tile_idx: tile index (0-24) corresponding to a board position
    :type from_tile_idx: byte
    :param to_tile_idx: tile index (0-24) corresponding to a board position
    :type to_tile_idx: byte
    """
    living = get_live_pieces_enumeration_no_king(state)
    if get_king_tile_index(state) == from_tile_idx:
        # Maybe the king moved onto a dragon?
        if expanded_state[to_tile_idx] == DRAGON:
            # If so, capture the dragon.
            for j, idx_j in living:
                if idx_j == to_tile_idx + DRAGON_BASE:
                    state[j] = DEAD
                    break
        # Either way, move the king.
        _set_king_tile_index(state, to_tile_idx)
        expanded_state[from_tile_idx] = EMPTY
        expanded_state[to_tile_idx] = KING
    else:
        # Find the index and byte in 'state' of the moving piece.
        for i, idx_i in living:
            if idx_i % DRAGON_BASE == from_tile_idx:
                if idx_i == from_tile_idx:  # If it's a guard.
                    # Maybe the guard moved onto a dragon?
                    if expanded_state[to_tile_idx] == DRAGON:
                        # If so, capture the dragon.
                        for j, idx_j in living:
                            if idx_j == to_tile_idx + DRAGON_BASE:
                                state[j] = DEAD
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
    # Then, check again for cascading conversions.
    while True:
        converted_a_guard = False
        for i, guard_idx in get_live_guards_enumeration(state):
            if _is_guard_surrounded(expanded_state, guard_idx):
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
    from collections import OrderedDict
    moves = OrderedDict()
    moves['b'] = _check_below(expanded_state, tile_idx, [EMPTY])
    moves['l'] = _check_left(expanded_state, tile_idx, [EMPTY])
    moves['r'] = _check_right(expanded_state, tile_idx, [EMPTY])
    moves['a'] = _check_above(expanded_state, tile_idx, [EMPTY])
    return moves


def _capture_dragon_moves(expanded_state, moves):
    """
    Assumes 'moves' is a dictionary returned by _all_orthogonal_moves(), and
    that this function is called as part of determining possible king or guard
    moves for the king player.

    Then, 'moves' doesn't contain possible dragon captures. So, for each move
    in 'moves', if the move would land on a dragon, check the tiles surrounding
    the dragon to see if one of them contains the king or a guard. If so, one
    possible move is to capture the dragon.

    Modifies 'moves' to reflect the new possible moves, which is done by
    replacing the previous value for the corresponding key, then returns
    'moves'.

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param moves: a dictionary returned by _all_orthogonal_moves()
    :type moves: dict(char, (bool, bool, byte, char))
    :return: moves, but modified to reflect the new possible moves, which is
        done by replacing the previous value for the corresponding key
    :rtype: dict(char, (bool, bool, byte, char))
    """
    caps = {'l': False, 'r': False, 'a': False, 'b': False}

    _, _, left_idx, at_left = moves['l']
    if at_left == DRAGON and _is_dragon_surrounded(expanded_state, left_idx):
        moves['l'] = (True, True, left_idx, at_left)
        caps['l'] = True
    _, _, right_idx, at_right = moves['r']
    if at_right == DRAGON and _is_dragon_surrounded(expanded_state, right_idx):
        moves['r'] = (True, True, right_idx, at_right)
        caps['r'] = True
    _, _, above_idx, at_above = moves['a']
    if at_above == DRAGON and _is_dragon_surrounded(expanded_state, above_idx):
        moves['a'] = (True, True, above_idx, at_above)
        caps['a'] = True
    _, _, below_idx, at_below = moves['b']
    if at_below == DRAGON and _is_dragon_surrounded(expanded_state, below_idx):
        moves['b'] = (True, True, below_idx, at_below)
        caps['b'] = True
    return moves, caps


def _all_valid_non_forced_moves_for_king(state, expanded_state, king_tile_idx):
    """
    Returns a list of (<from-tile-index>, <to-tile-index>) pairs representing
    all the valid moves that the king can make. *** Assumes the given tile
    index is between 0-24, and that the king is actually on that tile, that
    it's the king player's turn, and that the king player has no forced
    moves. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_idx: tile index (0-24) corresponding to a board position
    :type king_tile_idx: byte
    :return: a list of (<from-tile-index>, <to-tile-index>) pairs representing
        all the valid moves the king can make
    :rtype: list((byte, byte))
    """
    moves = {'capture': [], 'threat': [], 'progress': [], 'other': []}
    orth_moves= _all_orthogonal_moves(expanded_state, king_tile_idx)
    orth_moves, caps = _capture_dragon_moves(expanded_state, king_tile_idx)

    for key, value in caps:
        if caps[key]:
            moves['capture'].append((king_tile_idx, orth_moves[key][2]))


    # Moves doesn't contain possible jumps over guards. So, for each move, if
    # the move would land on a guard, replace it with a move that may jump over
    # the guard, if applicable.
    _, _, left_idx, at_left = orth_moves['l']
    if at_left == GUARD:
        # King can't both move left and jump over on left, so just replace.
        orth_moves['l'] = _check_left(expanded_state, left_idx, [EMPTY])
    _, _, right_idx, at_right = orth_moves['r']
    if at_right == GUARD:
        # King can't both move right and jump over on right, so just replace.
        orth_moves['r'] = _check_right(expanded_state, right_idx, [EMPTY])
    _, _, above_idx, at_above = orth_moves['a']
    if at_above == GUARD:
        # King can't both move up and jump over upwards, so just replace.
        orth_moves['a'] = _check_above(expanded_state, above_idx, [EMPTY])
    _, _, below_idx, at_below = orth_moves['b']
    if at_below == GUARD:
        # King can't both move down and jump over downwards, so just replace.
        orth_moves['b'] = _check_below(expanded_state, below_idx, [EMPTY])

    if orth_moves['b'][1]:
        moves['progress'].append((king_tile_idx, orth_moves['b'][2]))

    # Check for threatenedness here and append those to 'threat'
    for key, value, in  orth_moves:
        temp_state = copy.deepcopy(state)
        temp_expanded_state = copy.deepcopy(expanded_state)
        move_piece(temp_state, temp_expanded_state, orth_moves[key][0], orth_moves[key][1])
        guard_threat = is_guard_threatened(temp_state, temp_expanded_state)
        dragon_threat = is_dragon_threatened(temp_state, temp_expanded_state)
        if guard_threat or dragon_threat:
            moves['threat'].append((king_tile_idx, value[2]))
        else:
            moves['other'].append((king_tile_idx, value[2]))

    # Append all others to 'other'
    return moves
    # return [(king_tile_idx, tile_idx) for _, is_valid, tile_idx, _ in
    #         moves.values() if is_valid]


def count_king_moves(state, expanded_state, king_tile_idx):
    """
    Returns the number of valid moves the king can make, including checks for
    any possible forced moves.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param king_tile_idx: tile index (0-24) corresponding to a board position
    :type king_tile_idx: byte
    :return: the number of valid moves the king can make
    """
    king_is_captured, king_player_turn, forced_moves = \
        _is_king_captured(state, expanded_state, king_tile_idx)
    if king_is_captured:  # No forced moves. Doesn't matter the player's turn.
        # Set the terminal state bits, for efficiency.
        _mark_as_winning_state(state)
        _set_winner(state, DRAGON_PLAYER)
        return 0
    if king_player_turn and forced_moves is not None:
        # If the king is forced to make a move.
        return len([from_tile_idx for from_tile_idx, _ in forced_moves
                    if from_tile_idx == king_tile_idx])  # Return those.
    # Otherwise, it's the dragon player's turn or there are no forced moves, so
    # all other valid moves are possible.
    return len(_all_valid_non_forced_moves_for_king(expanded_state,
                                                    king_tile_idx))


def _all_valid_moves_for_guard(state, expanded_state, tile_idx):
    """
    Returns a list of (<from-tile-index>, <to-tile-index>) pairs representing
    all the valid moves that the guard at the given tile index can make.
    *** Assumes the given tile index is between 0-24, and that a guard is
    actually on that tile, that it's the king player's turn, and that the king
    player has no forced moves. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of (<from-tile-index>, <to-tile-index>) pairs representing
        all the valid moves the guard at the given tile index can make
    :rtype: list((byte, byte))
    """
    moves = {'capture': [], 'threat': [], 'progress': [], 'other': []}
    orth_moves = _all_orthogonal_moves(expanded_state, tile_idx)

    orth_moves, caps = _capture_dragon_moves(expanded_state, tile_idx)

    for key, value in caps:
        if caps[key]:
            moves['capture'].append((tile_idx, orth_moves[key][2]))
        else:
            temp_state = copy.deepcopy(state)
            temp_expanded_state = copy.deepcopy(expanded_state)
            move_piece(temp_state, temp_expanded_state, orth_moves[key][0], orth_moves[key][1])
            guard_threat = is_guard_threatened(temp_state, temp_expanded_state)
            dragon_threat = is_dragon_threatened(temp_state, temp_expanded_state)
            if guard_threat or dragon_threat:
                moves['threat'].append((tile_idx, orth_moves[key][2]))
            else:
                moves['other'].append((tile_idx, orth_moves[key][2]))

    # Check for threatenedness here and append those to 'threat'


    # Append all others to 'other'

    return moves
    # return [(tile_idx, to_tile_idx) for _, is_valid, to_tile_idx, _ in
    #         _capture_dragon_moves(expanded_state, moves).values() if is_valid]


def _all_valid_moves_for_dragon(expanded_state, tile_idx):
    """
    Returns a list of (<from-tile-index>, <to-tile-index>) pairs representing
    all the valid moves that the dragon at the given tile index can make.
    *** Assumes the given tile index is between 0-24, and that a dragon is
    actually on that tile, and that it's the dragon player's turn. ***

    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: tile index (0-24) corresponding to a board position
    :type tile_idx: byte
    :return: a list of (<from-tile-index>, <to-tile-index>) pairs representing
        all the valid moves the dragon at the given tile index can make
    :rtype: list((byte, byte))
    """
    moves = _all_orthogonal_moves(expanded_state, tile_idx)
    # Moves doesn't contain possible diagonal moves, so check those and add
    # them in if applicable.
    on_board, _, left_idx, _ = moves['l']
    if on_board:
        moves['al'] = _check_above(expanded_state, left_idx, [EMPTY])
        moves['bl'] = _check_below(expanded_state, left_idx, [EMPTY])
    on_board, _, right_idx, _ = moves['r']
    if on_board:
        moves['ar'] = _check_above(expanded_state, right_idx, [EMPTY])
        moves['br'] = _check_below(expanded_state, right_idx, [EMPTY])
    return [(tile_idx, to_tile_idx) for _, is_empty, to_tile_idx, _ in
            moves.values() if is_empty]


def ordered_dragon_moves(state,expanded_state,tile_idx):
    """
    Returns the list of ordering dragon moves: capturing, threatening.
    :param state: the current game state - current node 
    type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param tile_idx: the tile index of a dragon
    :type tile_idx: byte
    :return: the list of ordering dragon moves: capturing, threatening.
    :rtype: list ((byte,byte))
    """
    moves = _all_valid_moves_for_dragon(expanded_state,tile_idx)
    ordered_moves = []
    king_pos = get_king_tile_index(state)
    alive_guards = get_live_guards_enumeration(state)
    for m in moves:
        temp_state = copy.deepcopy(state)
        temp_expanded_state = copy.deepcopy(expanded_state)
        move_piece(temp_state,temp_expanded_state,\
                    m[0],m[1])
        if _is_king_captured(temp_state,temp_expanded_state,\
                                                king_pos):
            ordered_moves.append(m)
    potential_moves = [m for m in moves if m not in ordered_moves]
    for m in potential_moves:
        temp_state = copy.deepcopy(state)
        temp_expanded_state = copy.deepcopy(expanded_state)
        move_piece(temp_state,temp_expanded_state,\
                    m[0],m[1])
        for g in alive_guards:
            if _is_guard_surrounded(temp_expanded_state,g[1]):
                ordered_moves.append(m)
    potential_moves = [m for m in moves if m not in ordered_moves]
    for m in potential_moves:
        temp_state = copy.deepcopy(state)
        temp_expanded_state = copy.deepcopy(expanded_state)
        move_piece(temp_state, temp_expanded_state,\
                        m[0],m[1])
        #Because the dragon moves from m[0] to m[1].The tile_idx of
        #this dragon is updated to m[1]. Generate next_moves from m[1].
        #If any move in next_moves allows DRAGON to capture KING or GUARD
        #then m which is moving DRAGON to m[1] is a threatening move.
        next_moves = _all_valid_moves_for_dragon(temp_expanded_state,\
                                                            m[1])
        # TODO I feel like there's a bug here. We're iterating over moves,
        # but not actually using the move to determine if the king if captured.
        for next_m in next_moves:
            if _is_king_captured(temp_state,temp_expanded_state,\
                                                king_pos):
                ordered_moves.append(m)
    potential_moves = [m for m in moves if m not in ordered_moves]
    for m in potential_moves:
        temp_state = copy.deepcopy(state)
        temp_expanded_state = copy.deepcopy(state)
        move_piece(temp_state, temp_expanded_state,\
                        m[0], m[1])
        next_moves = _all_valid_moves_for_dragon(temp_expanded_state,\
                                                            m[1])
        for next_m in next_moves:
            for g in alive_guards:
                if _is_guard_surrounded(temp_expanded_state,g[1]):
                    ordered_moves.append(m)
    potential_moves = [m for m in moves if m not in ordered_moves]
    for m in potential_moves:
        ordered_moves.append(m)
    return ordered_moves


def all_valid_moves(state, expanded_state):
    """
    Returns a list of (<from-tile-index>, <to-tile-index>) pairs representing
    all the valid moves that every piece that is alive can make in the given
    state, depending on which player's turn it is.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a list of (<from-tile-index>, <to-tile-index>) pairs representing
        all the valid moves that every piece that is alive can make in the
        given state, depending on which player's turn it is
    :rtype: list((byte, byte))
    """
    all_moves = []
    king_progress = []
    captures = []
    threats = []
    other_moves = []
    if is_winning_state(state):  # Check if result has already been computed.
        return all_moves
    king_tile_idx = get_king_tile_index(state)
    king_is_captured, king_player_turn, forced_moves = \
        _is_king_captured(state, expanded_state, king_tile_idx)
    if king_is_captured:  # No forced moves. Doesn't matter the player's turn.
        # Set the terminal state bits, for efficiency.
        _mark_as_winning_state(state)
        _set_winner(state, DRAGON_PLAYER)
        return all_moves
    if king_player_turn:
        if forced_moves is not None:  # If the king is forced to make a move.
            return forced_moves  # Return those.
        # Otherwise, there are no forced moves, so get all other valid moves.

        # We get dicts back now with capture, threat, progress, other
        king_moves = _all_valid_non_forced_moves_for_king(state, expanded_state,
                                                              king_tile_idx)
        guard_moves = []
        for _, idx in get_live_guards_enumeration(state):
            guard_moves.append(_all_valid_moves_for_guard(expanded_state, idx))

        # order moves as progress, capture, threat, other
        all_moves.extend(king_moves['progress'])
        all_moves.extend(king_moves['capture'])
        for guard in guard_moves:
            all_moves.extend(guard['capture'])
        all_moves.extend(king_moves['threat'])
        for guard in guard_moves:
            all_moves.extend(guard['threat'])
        all_moves.extend(king_moves['other'])
        for guard in guard_moves:
            all_moves.extend(guard['other'])

        # all_moves.extend(_all_valid_non_forced_moves_for_king(expanded_state,
        #                                                       king_tile_idx))
        # for _, idx in get_live_guards_enumeration(state):
        #     all_moves.extend(_all_valid_moves_for_guard(expanded_state, idx))
    else:  # It's DRAGON_PLAYER's turn, so no forced moves.
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
    if is_winning_state(state):  # Check if result has already been computed.
        if who_won(state) == KING_PLAYER:
            return True, KING_WIN
        else:
            return True, DRAGON_WIN
    king_tile_idx = get_king_tile_index(state)
    if king_tile_idx % 5 == 0:  # If the king is on the last rank.
        _mark_as_winning_state(state)
        _set_winner(state, KING_PLAYER)
        return True, KING_WIN  # Then it's a win for the king player.
    king_is_captured, king_player_turn, forced_moves = \
        _is_king_captured(state, expanded_state, king_tile_idx)
    if king_is_captured:  # If the king is captured.
        _mark_as_winning_state(state)
        _set_winner(state, DRAGON_PLAYER)
        return True, DRAGON_WIN  # Then it's a win for the dragon player.
    if king_player_turn:  # If it's the king player's turn.
        if forced_moves is not None:  # If he has forced moves, he can move, so
            # since he is not on the last rank and is not captured, it is not
            # a terminal state.
            return False, 0
        # Otherwise, the king is not on the last rank, and also not captured,
        # so it's a draw iff the king player has no possible valid moves.
        if len(_all_valid_non_forced_moves_for_king(expanded_state,
                                                    king_tile_idx)) == 0:
            # King has no valid moves, but the guards still might.
            has_moves = False
            for _, idx in get_live_guards_enumeration(state):
                if _all_valid_moves_for_guard(expanded_state, idx):
                    has_moves = True
                    break
            if not has_moves:  # There are no possible guard moves either.
                # mark_as_winning_state(state)  # TODO: so rename to mark_as_terminal_state()?
                return True, DRAW  # It's a draw, NOT a win for dragon player.
    else:  # It's the dragon player's turn, and the king is not captured, and
        # the king player has not won, then it's a draw iff the dragon player
        # has no possible valid moves.
        has_moves = False
        for _, idx in get_live_dragon_enumeration(state):
            if _all_valid_moves_for_dragon(expanded_state, idx - DRAGON_BASE):
                has_moves = True
                break
        if not has_moves:  # There are no possible moves for the dragon player.
            # mark_as_winning_state(state)  # TODO: so rename to mark_as_terminal_state()?
            return True, DRAW  # It's a draw, NOT a win for the king player.
    return False, 0



def successors(state, expanded_state):
    """
    Returns a list of (<successor-state>, <successor-expanded-state>, <move>)
    tuples, one tuple for each successor of the given state, where 'move' is
    itself a (<from-tile-index>, <to-tile-index>) pair.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a list of (<successor-state>, <successor-expanded-state>, <move>)
        tuples, one tuple for each successor of the given state
    :rtype: list((array of bytes, dict(byte, char), (byte, byte)))
    """
    all_successors = []
    for from_tile_idx, to_tile_idx in all_valid_moves(state, expanded_state):
        new_state = copy.deepcopy(state)
        new_expanded_state = create_expanded_state_representation(new_state)
        move_piece(new_state, new_expanded_state, from_tile_idx, to_tile_idx)
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
    return '.'.join('{:x}'.format(b) if i > 0
                    else '{:x}'.format(int(b) & INDEX_AND_TURN_MASK)
                    for i, b in enumerate(state))
