from array import array
from state import *
"""
We've got 0-24 as guard positions and 25 as alive/dead
and we've got 100-124 as dragon positions 125 as alive/dead.
unit_array is an array of bytes where unit_array[0] is the king.
The guard will come in the next three places and the final 5 
indices will be the dragons.

5   .  .  K  .  . 
4   .  G  G  G  .
3   .  .  .  .  . 
2   D  D  D  D  D
1   .  .  .  .  .

    A  B  C  D  E

This is how the board should be drawn.
Internally, the board is represented by converting the state (as a byte array),
to a list of 5 lists of strings, as such:

    0 : 0 1 2 3 4
    1 : 0 1 2 3 4
    2 : 0 1 2 3 4
    4 : 0 1 2 3 4

"""

_SPACES = ' '
_CHARS = [ 'A', 'B', 'C', 'D', 'E' ]
_NUMBERS = [ '5', '4', '3', '2', '1' ]
_BLANK = ' '
_G = 'G'
_D = 'D'
_K = 'K'

def get_pos(pos):
    """
    Convert an integer 0-24 representing a place on the board into an integer 
    which corresponds to the same location on a board with a "list of list"
    representation.
    :return: The offsets of the row and columns of the board location.
    :rtype: (Int, Int)
    """
    if pos > 100:
        pos = pos % 100
    if pos >= 25:
        return None
    col = int(pos / 5)
    pos = pos % 5
    row = abs(pos - 4)
    return (row, col)

def draw_board(state):
    """
    Draw the board from a state.
    :param state: A game state encoded in an array of 9 bytes.
    :type state: State
    """
    board = []
    for row in range(BOARD_NUM_ROWS):
        board.append([])
        for _ in range(BOARD_NUM_COLS):
            board[row].append(_BLANK)
    
    king_pos = get_king_number(state)
    row, col = get_pos(king_pos)
    board[row][col] = _K

    guard_inds = get_live_guards_indices(state)
    for i in guard_inds:
        row, col = get_pos(state[i])
        board[row][col] = _G

    dragon_inds = get_live_dragon_indices(state)
    for i in dragon_inds:
        row, col = get_pos(state[i] % DRAGON_BASE)
        board[row][col] = _D

    for i in range(len(board)):
        print(_NUMBERS[i] + _SPACES, end='')
        print(  _SPACES + board[i][0] + _SPACES + \
                _SPACES + board[i][1] + _SPACES + \
                _SPACES + board[i][2] + _SPACES + \
                _SPACES + board[i][3] + _SPACES + \
                _SPACES + board[i][4] + _SPACES)
    # print('')
   
    print(' ' + _SPACES, end='')
    for c in _CHARS:
        print(_SPACES + c + _SPACES, end='')
    print('')

draw_board(DEFAULT_INITIAL_STATE)
    
    
