from ui import *
from minimax import *
from time import sleep
from evaluations import simple_eval
from utils import record_move_search_time
from search import iterative_deepening_search


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


def next_move(state, expanded_state, from_human, evaluate, search, age,
              max_depth):
    """
    Returns the next move to be played for this ply, either from a human or
    else from the AI.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param from_human: should we get the next move from a human?
    :type from_human: bool
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param age: an age counter, which increases (outside of calls to next_move)
        whenever a move is made that captures a piece
    :type age: int
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: a valid move as a (<from-tile-index>, <to-tile-index>) pair
    :rtype: (byte, byte)
    """
    if from_human:
        return get_player_move(state, expanded_state)
    else:
        from threading import Thread

        class MyThread(Thread):
            def __init__(self):
                Thread.__init__(self)
                self._results = None

            def run(self):
                from time import clock
                start_t = clock()
                results = iterative_deepening_search(state, expanded_state,
                                                     evaluate, search, age,
                                                     max_depth)
                runtime = clock() - start_t
                self._results = (results, runtime)

            def result(self):
                return self._results

        thread = MyThread()
        thread.start()
        print("Deciding on a move.", end='', flush=True)
        while thread.is_alive():
            sleep(1)
            print(".", end='', flush=True)
        print('', flush=True)
        thread.join()
        ((utility, exact), move), time = thread.result()
        print("After", time, "seconds, the chosen move is:",
              string_position(move[0]) + string_position(move[1]))
        print("Move utility:", utility, "(exact)" if exact else "(estimated)")
        record_move_search_time(time, evaluate, search, max_depth)
        return move


def play_ply(state, expanded_state, for_human, pause_for, move_number,
             evaluate, search, age, max_depth):
    """
    Executes a full game ply either for a human player or for the AI. Returns
    True iff the game has reached a terminal state as a result of the ply.

    :param state: a compact state representation
    :type state: array of bytes
    :param expanded_state: the expanded representation of the state
    :type expanded_state: dict(byte, char)
    :param for_human: is this ply played by a human?
    :type for_human: bool
    :param pause_for: number of seconds to pause for after getting the move
        from the human player or the AI before actually making the move
    :type pause_for: int or float
    :param move_number: which move is this in the game?
    :type move_number: int
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param age: an age counter, which increases (outside of calls to play_ply)
        whenever a move is made that captures a piece
    :type age: int
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: True iff the game has reached a terminal state
    :rtype: bool
    """
    draw_board(state, move_number)
    from_tile_idx, to_tile_idx = next_move(state, expanded_state, for_human,
                                           evaluate, search, age, max_depth)
    sleep(pause_for)
    move_piece(state, expanded_state, from_tile_idx, to_tile_idx)
    print('')
    print('')
    terminal, utility = is_terminal(state, expanded_state)
    if terminal:
        draw_board(state, move_number, terminal, utility)
        print("Thanks for playing!")
    return terminal


def play(player_2_is_human, player_1_is_human, evaluate, search, max_depth,
         pause_for=0):
    """
    A game loop that has either a human player or the AI playing interactively
    against another human or the AI itself. Recall that player 2 plays first!

    :param player_2_is_human: True iff the a human is controlling player 2
    :type player_2_is_human: bool
    :param player_1_is_human: True iff the a human is controlling player 1
    :type player_1_is_human: bool
    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param pause_for: number of seconds to pause for after getting the move
        from the human player or the AI before actually making the move;
        defaults to 0
    :type pause_for: int or float
    """
    age = 0
    move_number, state, expanded_state = setup_game()
    while True:
        num_guards = len(get_live_guards_enumeration(state))
        num_dragons = len(get_live_dragon_enumeration(state))
        if play_ply(state, expanded_state, player_2_is_human, pause_for,
                    move_number, evaluate, search, age, max_depth):
            break
        if play_ply(state, expanded_state, player_1_is_human, pause_for,
                    move_number, evaluate, search, age, max_depth):
            break
        if num_guards != len(get_live_guards_enumeration(state)) or \
                num_dragons != len(get_live_dragon_enumeration(state)):
            age += 1
        move_number += 1


def play_single_player(evaluate, search, max_depth):
    """
    A game loop that has a human player playing interactively against the AI.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
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
    play(player_choice == "d", player_choice != "d", evaluate, search,
         max_depth)


def play_two_player(evaluate, search, max_depth):
    """
    A game loop that has a two human players playing against each other.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    """
    print('')
    play(True, True, evaluate, search, max_depth)


def play_ai_only(evaluate, search, max_depth):
    """
    A game loop that has the AI playing against itself, and displaying the
    game to onlookers.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, an age, a remaining depth, and returning a
        ((<utility>, <exact>), <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int,
                   int) => ((numeric, bool), (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    """
    while True:
        pause_for = input("How long to pause between moves? [non-negative] ")
        try:
            pause_for = float(pause_for)
            if pause_for < 0:
                print("Invalid duration:", pause_for)
            else:
                break
        except ValueError:
            print("Invalid duration: '" + pause_for + "'")
    print('')
    play(False, False, evaluate, search, max_depth, pause_for)


if __name__ == "__main__":
    print("Welcome to madking!")
    print("We hope you have fun playing 'The Mad King!' game!")
    print('')
    while True:
        mode = input("Single Player, Two Player, or AI Only Mode? [s/t/a] ")
        if mode in ["s", "t", "a"]:
            break
        print("Invalid choice: '" + mode + "'")
    if mode == "s":
        play_single_player(simple_eval, minimax, DEFAULT_DEPTH_LIMIT)
    elif mode == "t":
        play_two_player(simple_eval, minimax, DEFAULT_DEPTH_LIMIT)
    else:
        play_ai_only(simple_eval, minimax, DEFAULT_DEPTH_LIMIT)
