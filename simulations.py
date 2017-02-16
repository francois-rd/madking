from state import *
from math import floor
from ui import draw_board
from utils import parse_move


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
    move_number = 1
    draw_board(state, False, move_number)
    expanded_state = create_expanded_state_representation(state)
    for m in moves:
        move_number += 0.5
        correct_form, from_tile_idx, to_tile_idx = parse_move(m)
        if not correct_form:
            print("Wrong move format:", m)
            print("Stopping the simulation.")
            break
        if (from_tile_idx, to_tile_idx) not in all_valid_moves(state,
                                                               expanded_state):
            print("Bad move:", m)
            print("Stopping the simulation.")
            break
        print("The move is:", m)
        move_piece(state, expanded_state, from_tile_idx, to_tile_idx)
        print('')
        print('')
        draw_board(state, False, int(floor(move_number)))
        terminal, utility = is_terminal(state, expanded_state)
        if terminal:
            print("Terminal state with utility:", utility)
            break


if __name__ == "__main__":
    game_state = get_default_game_start()
    run_the_game_simulation(game_state, ['C2C3', 'D4E4', 'E2E3', 'C5D5'])
