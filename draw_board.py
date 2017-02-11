from array import array
import state
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
_BLANK = '.'

def draw_board(state):
    """
    :param state: A game state encoded in an array of 9 bytes.
    :type state: State
    """

    board = 5*[5*[_BLANK]]
    
    king_pos = state.get_king_number(state)
    guard_pos = state.get_live_guard_indices(state)
    dragon_pos = state.get_live_dragon_indices(state)
    
    print(king_pos, guard_pos, dragon_pos)

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

draw_board(state.create_state_from(state.TURN_MASK, state.DEFAULT_INITIAL_STATE))
    
    
