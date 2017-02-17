from ui import *
from minimax import *
from evaluations import simple_eval


def setup_game():
    """
    Sets up the game at the start. Prints 'Let's play!' to standard output,
    then returns (<move-number>, <state>, <expanded-state>) corresponding to
    the default game start.

    :return: (<move-number>, <state>, <expanded-state>) corresponding to the
        default game start
    :rtype: (int, array of bytes, dict(byte, char))
    """
    print("Let's play!")
    print('')
    print('')
    move_number = 1
    state = get_default_game_start()
    expanded_state = create_expanded_state_representation(state)
    return move_number, state, expanded_state


def next_move(state, expanded_state, from_human):
    """
    Returns the next move to be played for this ply, either from a human or
    else from the AI.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param from_human: should we get the next move from a human?
    :type from_human: bool
    :return: a valid move as a (<from-tile-index>, <to-tile-index>) pair
    :rtype: (byte, byte)
    """
    if from_human:
        return get_player_move(state, expanded_state)
    else:
        move = minimax(state, expanded_state, simple_eval,
                       DEFAULT_DEPTH_LIMIT)[1]
        print("The move is:", string_position(move[0]) +
              string_position(move[1]))
        return move


def play_ply(state, expanded_state, for_human, move_number):
    """
    Executes a full game ply either for a human player or for the AI. Returns
    True iff the game has reached a terminal state as a result of the ply.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param for_human: is this ply played by a human?
    :type for_human: bool
    :param move_number: which move is this in the game?
    :type move_number: int
    :return: True iff the game has reached a terminal state
    :rtype: bool
    """
    draw_board(state, move_number)
    from_tile_idx, to_tile_idx = next_move(state, expanded_state, for_human)
    move_piece(state, expanded_state, from_tile_idx, to_tile_idx)
    print('')
    print('')
    terminal, utility = is_terminal(state, expanded_state)
    if terminal:
        draw_board(state, move_number, terminal, utility)
        print("Thanks for playing!")
    return terminal


def play_single_player():
    """
    A game loop that has a human player playing interactively against the AI.
    """
    while True:
        player_choice = input("King or Dragon Player? [k/d] ")
        if player_choice in ["k", "d"]:
            break
        print("Invalid choice: '" + player_choice + "'")
    print('')
    if player_choice == "d":
        print("You're the Dragon Player, so you play first!")
    else:
        print("You're the King Player, so you play second!")
    move_number, state, expanded_state = setup_game()
    while True:
        if play_ply(state, expanded_state, player_choice == "d", move_number):
            break
        if play_ply(state, expanded_state, player_choice != "d", move_number):
            break
        move_number += 1


def play_two_player():
    """
    A game loop that has a two human players playing against each other.
    """
    move_number, state, expanded_state = setup_game()
    while True:
        if play_ply(state, expanded_state, True, move_number):
            break
        if play_ply(state, expanded_state, True, move_number):
            break
        move_number += 1


if __name__ == "__main__":
    print("Welcome to madking!")
    print("We hope you have fun playing 'The Mad King!' game!")
    print('')
    while True:
        mode = input("Single or Two Player Mode? [s/t] ")
        if mode in ["s", "t"]:
            break
        print("Invalid choice: '" + mode + "'")
    if mode == "s":
        play_single_player()
    else:
        play_two_player()
