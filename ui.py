from state import *
from sys import stdout
from utils import *

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

_SPACE = ' '
_C_RED = '\033[91m'
_C_GREEN = '\33[32m'
_C_MAGENTA = '\33[34m'
_C_END = '\033[0m'


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


def draw_board(state, move_number, terminal=False, utility=0):
    """
    Draws the board from the given state representation to standard output.
    Board is green coloured, if it's KING turn.
    Board is red coloured, if it's DRAGON turn.

    :param state: a compact state representation
    :type state: array of bytes
    :param move_number: the count of the moves so far in the game
    :type move_number: int
    :param terminal: is the given state a terminal state?
    :type terminal: bool
    :param utility: the utility value of the state **if the state is terminal**
    :type utility: int
    """
    if terminal:
        if utility == KING_WIN:
            print("The king player has won!")
        elif utility == DRAGON_WIN:
            print("The dragon player has won!")
        else:
            print("It's a draw!")
        if stdout.isatty():
            print(_C_MAGENTA, end='')
    else:
        if player_turn(state) == KING_PLAYER:
            print("Move:", move_number, "(king player's turn)")
            if stdout.isatty():
                print(_C_GREEN, end='')
        else:
            print("Move:", move_number, "(dragon player's turn)")
            if stdout.isatty():
                print(_C_RED, end='')

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
        print(RANK[i] + OFF_THE_BOARD, end='')
        for tile_content in rank:
            print(_SPACE + tile_content, end='')
        print('')
    print('')

    print(OFF_THE_BOARD + OFF_THE_BOARD, end='')
    for f in FILE:
        print(OFF_THE_BOARD + f, end='')
    print('')
    if stdout.isatty():
        print(_C_END, end='')
    print()


def get_player_move(state, expanded_state):
    """
    Prompts the player to enter a move, then validates the move. Repeats if the
    move is not valid. Returns a valid move as a (<from-tile-index>,
    <to-tile-index>) pair.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :return: a valid move as a (<from-tile-index>, <to-tile-index>) pair
    :rtype: (byte, byte)
    """
    while True:
        move = input("Enter your move: ")
        correct_form, from_tile_idx, to_tile_idx = parse_move(move)
        if not correct_form:
            print("Wrong move format: '" + move + "'.")
            continue
        if (from_tile_idx, to_tile_idx) not in all_valid_moves(state,
                                                               expanded_state):
            print("Invalid move: '" + move + "'.")
            continue
        return from_tile_idx, to_tile_idx
