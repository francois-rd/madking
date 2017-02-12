from state import *

"""
This is how the board should be drawn.

5  . . K . .
4  . G G G .
3  . . . . .
2  D D D D D
1  . . . . .

   A B C D E

Internally, the board is represented by converting the state (as a byte array),
to a list of 5 lists of strings, as such:

    0 : 0 1 2 3 4
    1 : 0 1 2 3 4
    2 : 0 1 2 3 4
    4 : 0 1 2 3 4

"""

_FILE = ['A', 'B', 'C', 'D', 'E']
_RANK = ['5', '4', '3', '2', '1']


def get_pos(tile_idx):
    """
    Converts a tile index into (row, col) pair, which are the indices into the
    list of list of string representation of the board corresponding to the
    same position.

    :param tile_idx: position of the piece as in number from 0 to 24
    :type tile_idx: byte
    :return: the offsets of the row and columns of the board location
    :rtype: (int, int)
    """
    return abs(tile_idx % BOARD_NUM_RANKS - 4), tile_idx // BOARD_NUM_RANKS


def draw_board(state):
    """
    Draws the board from the given state representation to standard output.

    :param state: a compact state representation
    :type state: array of bytes
    """
    board = [[EMPTY] * BOARD_NUM_FILES for _ in range(BOARD_NUM_RANKS)]

    row, col = get_pos(get_king_tile_index(state))
    board[row][col] = KING

    for _, guard_idx in get_live_guards_enumeration(state):
        row, col = get_pos(guard_idx)
        board[row][col] = GUARD

    for _, dragon_idx in get_live_dragon_enumeration(state):
        row, col = get_pos(dragon_idx - DRAGON_BASE)
        board[row][col] = DRAGON

    for i, rank in enumerate(board):
        print(_RANK[i] + OFF_THE_BOARD, end='')
        for tile_content in rank:
            print(OFF_THE_BOARD + tile_content, end='')
        print('')
    print('')

    print(OFF_THE_BOARD + OFF_THE_BOARD, end='')
    for f in _FILE:
        print(OFF_THE_BOARD + f, end='')
    print('')


if __name__ == "__main__":
    draw_board(DEFAULT_INITIAL_STATE)
