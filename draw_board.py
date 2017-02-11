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
"""

_SPACES = ' '
_CHARS = [ 'A', 'B', 'C', 'D', 'E' ]
_NUMBERS = [ '5', '4', '3', '2', '1' ]
_BLANK = ' '
_G = 'G'
_D = 'D'
_K = 'K'

def get_pos(pos):
    if pos < 5:
        col = 0
    elif pos < 10:
        col = 1
    elif pos < 15:
        col = 2
    elif pos < 20:
        col = 3
    else:
        col = 4

    pos = pos % 5

    if pos == 4: 
        row = 0
    elif pos == 3: 
        row = 1
    elif pos == 2: 
        row = 2
    elif pos == 1:
        row = 3
    else:
        row = 4

    return row, col

def draw_board(state):
    """
    :param state: A game state encoded in an array of 9 bytes.
    :type state: State
    """

    board = []
    for i in range(BOARD_NUM_ROWS):
        board.append([])
        for j in range(BOARD_NUM_COLS):
            board[i].append(_BLANK)
    
    king_pos = get_king_number(state)
    row, col = get_pos(king_pos)
    board[row][col] = _K

    guard_inds = get_live_guards_indices(state)
    for i in guard_inds:
        row, col = get_pos(state[i])
        board[row][col] = _G

    dragon_inds = get_live_dragon_indices(state)
    for i in dragon_inds:
        row, col = get_pos(state[i] % 100)
        board[row][col] = _D

    for i in range(len(board)):
        print(_NUMBERS[i] + _SPACES, end='')
        print(  _SPACES + board[i][0] + _SPACES + \
                _SPACES + board[i][1] + _SPACES + \
                _SPACES + board[i][2] + _SPACES + \
                _SPACES + board[i][3] + _SPACES + \
                _SPACES + board[i][4] + _SPACES)
    print('')
   
    print(' ' + _SPACES, end='')
    for c in _CHARS:
        print(_SPACES + c + _SPACES, end='')
    print('')

draw_board(DEFAULT_INITIAL_STATE)
    
    
