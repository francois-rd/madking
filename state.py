from array import array

"""
Index of each board square.

5   4  9  K 19 24
4   3  G  G  G 23
3   2  7 12 17 22
2   D  D  D  D  D
1   0  5 10 15 20

    A  B  C  D  E


State representation of the board.

array: | K | O | O | O | O | O | O | O | O |
         0   1   2   3   4   5   6   7   8

Each element in the board array has an integer that fits in one byte.
The king (K) is always at state[0].
The remaining 8 elements have either a guard (G) or a dragon (D).
The value in the element is 0-25 for a guard, 0-24 is the position, and 25
means is dead.
The value in the element is 25 or 100-124 for a dragon, 100-124 is the
position + 100, and 25 means is dead.
The first 5 bits of state[0] contain an integer 0-24, which is the position of
the king.
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
BOARD_NUM_ROWS = BOARD_NUM_COLS = 5
DRAGON_PLAYER = 2
STATE_SIZE = 9
DRAGON_START_INDEX = 4
DEAD = 25
DRAGON_BASE = 100
NUM_META_STATE_BITS = 3
TURN_MASK = 0b00000100
WIN_MASK = 0b00000010
WHO_WON_MASK = 0b00000001
ALL_META_STATE_MASK = TURN_MASK | WIN_MASK | WHO_WON_MASK

DEFAULT_KING_PLUS_META_STATE_BYTE = 0b01110000
DEFAULT_INITIAL_STATE = array('B', [DEFAULT_KING_PLUS_META_STATE_BYTE,
                                    8, 13, 18, 101, 106, 111, 116, 121])

_ord_a = ord('A')
_ord_1 = ord('1')


def create_state_from(who_s_turn, initial_positions_as_numbers):
    base_num = initial_positions_as_numbers[0]
    initial_positions_as_numbers[0] = ((base_num << 1) | (who_s_turn % 2)) << 2
    return array('B', initial_positions_as_numbers)


def get_live_pieces_indices_no_king(state):
    return [i for i in range(1, STATE_SIZE) if state[i] != DEAD]


def get_live_guards_indices(state):
    return [i for i in range(1, DRAGON_START_INDEX) if state[i] < DEAD]


def get_live_dragon_indices(state):
    return [i for i in range(DRAGON_START_INDEX, STATE_SIZE)
            if DRAGON_BASE <= state[i]]


def number(pos):
    """
    :param pos: Position of the piece represented in 'A1' to 'E5'
    :return: The position as in number from 0 to 24
    """
    return (ord(pos[0]) - _ord_a) * BOARD_NUM_ROWS + ord(pos[1]) - _ord_1


def position(num):
    """
    :param num: The position as in number from 0 to 24
    :return: Position of the piece represented in 'A1' to 'E5'
    """
    return chr((num // BOARD_NUM_ROWS) + _ord_a) + chr((num % BOARD_NUM_ROWS) +
                                                       _ord_1)


def get_king_number(state):
    return state[0] >> NUM_META_STATE_BITS


def set_king_number(state, num):
    state[0] = (num << NUM_META_STATE_BITS) | (state[0] & ALL_META_STATE_MASK)


def player_turn(state):
    if (state[0] & TURN_MASK) == 0:
        return DRAGON_PLAYER
    else:
        return KING_PLAYER


def is_winning_state(state):
    return (state[0] & WIN_MASK) != 0


def who_won(state):
    if (state[0] & WHO_WON_MASK) == 0:
        return DRAGON_PLAYER
    else:
        return KING_PLAYER


def move(state, from_pos, to_pos):
    """
    Assumes the move is valid. If it's a guard moving, and the guard would
    capture a dragon, the corresponding dragon is set to DEAD.

    :param state:
    :param from_pos:
    :param to_pos:
    :return:
    """
    from_num = number(from_pos)
    to_num = number(to_pos)
    if get_king_number(state) == from_num:
        set_king_number(state, to_num)
    else:
        living = get_live_pieces_indices_no_king(state)
        for i in living:
            if state[i] == from_num or state[i] == from_num + DRAGON_BASE:
                state[i] = to_num
                if i < DRAGON_START_INDEX:
                    for j in living:
                        if state[j] == to_num + DRAGON_BASE:
                            state[j] = DEAD
                            break
