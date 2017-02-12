from state import *
from sys import stdout

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
_FILE = ['A', 'B', 'C', 'D', 'E']
_RANK = ['5', '4', '3', '2', '1']
_C_RED = '\033[91m'
_C_GREEN = '\33[32m'
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


def draw_board(state):
    """
    Draws the board from the given state representation to standard output.
    Board is green coloured, if it's KING turn
    Board is red coloured, if it's DRAGON turn

    :param state: a compact state representation
    :type state: array of bytes
    """
    if player_turn(state) == KING_PLAYER:
        print("It's the king player's turn:")
        if stdout.isatty():
            print(_C_GREEN, end='')
    else:
        print("It's the dragon player's turn:")
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
        print(_RANK[i] + OFF_THE_BOARD, end='')
        for tile_content in rank:
            print(_SPACE + tile_content, end='')
        print('')
    print('')

    print(OFF_THE_BOARD + OFF_THE_BOARD, end='')
    for f in _FILE:
        print(OFF_THE_BOARD + f, end='')
    print('')
    if stdout.isatty():
        print(_C_END, end='')
    print()


def parse_move(str_move):
    """
    Parses a move given in a format similar to 'A2B3', which means "move the
    piece at tile 'A2' to tile 'B3'", into a <from-tile-index> and a
    <to-tile-index>. Returns the (True, <from-tile-index>, <to-tile-index>) if
    the move is correctly formatted, and (False, -1, -1) otherwise.

    :param str_move: a move given in a format similar to 'A2B3'
    :type str_move: string
    :return: the (True, <from-tile-index>, <to-tile-index>) if the move is
        correctly formatted, and (False, -1, -1) otherwise
    :rtype: (bool, int, int)
    """
    if len(str_move) != 4 or \
            str_move[0] not in _FILE or str_move[1] not in _RANK or \
            str_move[2] not in _FILE or str_move[3] not in _RANK:
        return False, -1, -1
    return True, tile_index(str_move[0:2]), tile_index(str_move[2:4])


def run_the_game_simulation(state, moves):
    """
    Executes all moves in the given list of moves, while alternating player
    turns, and prints the resulting boards and other game state information to
    standard output. Each move in the list should be in a format similar to
    'A2B3', which means "move the piece at tile 'A2' to tile 'B3'". Print an
    error message if the move is not valid.

    :param state: a compact state representation
    :type state: array of bytes
    :param moves: a list moves to execute
    :type moves: list(string)
    """
    print("Game is starting like this:")
    print('')
    draw_board(state)
    expanded_state = create_expanded_state_representation(state)
    for m in moves:
        correct_form, from_tile_idx, to_tile_idx = parse_move(m)
        if not correct_form:
            print("Wrong move format:", m)
            print("Stopping the simulation.")
            break
        if not is_valid_move(state, expanded_state, from_tile_idx,
                             to_tile_idx):
            print("Bad move:", m)
            print("Stopping the simulation.")
            break
        print("The move is:", m)
        move(state, expanded_state, from_tile_idx, to_tile_idx)
        print('')
        print('')
        draw_board(state)
        terminal, status = is_terminal(state, expanded_state)
        if terminal:
            print(status)
            break


if __name__ == "__main__":
    game_state = get_default_game_start()
    run_the_game_simulation(game_state, ['C2C3', 'D4E4', 'E2E3', 'C5D5'])
