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
C_RED = '\033[91m'
C_GREEN = '\33[32m'


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
    player_t = player_turn(state)
    if player_t == KING_PLAYER:
        color = C_GREEN
    else:
        color = C_RED

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
        print(color + _RANK[i] + OFF_THE_BOARD, end='')
        for tile_content in rank:
            print(color + OFF_THE_BOARD + tile_content, end='')
        print('')
    print('')

    print(OFF_THE_BOARD + OFF_THE_BOARD, end='')
    for f in _FILE:
        print(color + OFF_THE_BOARD + f, end='')
    print('')
    print()


def run_the_game_simulation(state, moves):
    """
    Outputs, and execute all the moves given in the moves, and print them on
    console.
    moves list should be of format, `A2B3` explaining move the piece at A2 to B3
    It is assumed list will have moves in order, such that it starts from dragon
    turn, followed by king's turn and cycle keeps on going.
    Print the big message if the move is not valid
    :param state: state on which moves will be executed
    :param moves: a list of all the moves needed to be executed
    :type: list
    """
    print("Game is starting like this")
    draw_board(state)
    expand_state = expand_state_representation(state)
    for m in moves:
        from_tile_index = tile_index(m[0:2])
        end_tile_index = tile_index(m[2:4])
        if not is_valid_move(expand_state, from_tile_index, end_tile_index):
            print("Bad happened at move " + m)
            print("Stopping the simulation")
            break
        move(state, expand_state, from_tile_index,
             end_tile_index)
        draw_board(state)
        change_player_turn(state)
        terminal, status = is_terminal(state, expand_state)
        if terminal:
            print(status)
            break


if __name__ == "__main__":
    game_state = get_default_game_start()
    run_the_game_simulation(game_state, ['C2C3', 'D4E4','E2E3', 'C5D5'])
