import argparse
from ui import *
from minimax import *
from time import sleep
from evaluations import simple_eval, split_weight_eval
from utils import record_move_data
from search import iterative_deepening_search
from TranspositionTable import TranspositionTable

defaults = {
    'eval': {
        'simple': simple_eval,
        'split': split_weight_eval
    },
    'eval_name': 'split',
    'search': {
        'minimax': minimax,
        'alpha-beta': alpha_beta
    },
    'ordered-search': {
        'minimax': minimax_ordered,
        'alpha-beta': alpha_beta_ordered
    },
    'search_name': 'alpha-beta',
    'depth': DEFAULT_DEPTH_LIMIT,
    'replace': {
        'overall-oldest': TranspositionTable.replace_overall_oldest,
        'older-else-overall-oldest':
            TranspositionTable.replace_older_value_or_else_overall_oldest,
        'older-else-new':
            TranspositionTable.replace_older_value_or_else_new_entry,
        'shallower-else-shallower-with-first': TranspositionTable.
            replace_shallower_value_or_else_shallower_with_first,
        'shallower-else-overall-oldest':
            TranspositionTable.replace_shallower_value_or_else_overall_oldest,
        'shallower-else-new':
            TranspositionTable.replace_shallower_value_or_else_new_entry,
    },
    'replace_name': 'overall-oldest',
    'table-size': 1000000
}


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


def next_move(state, expanded_state, from_human, evaluate, search, max_depth):
    """
    Returns (<move>, <time>, <utility>), where <move> is the next move to be
    played for this ply, either from a human or else from the AI, <time> is the
    time taken by the AI to decide on the move, and <utility> is the utility of
    the move. <move> and <utility> will both be None if the move was made by a
    human.

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
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: (<move>, <time>, <utility>)
    :rtype: ((byte, byte), float, float)
    """
    if from_human:
        return get_player_move(state, expanded_state), None, None
    else:
        from threading import Thread

        class MyThread(Thread):
            def __init__(self):
                Thread.__init__(self)
                self._results = None

            def run(self):
                from time import clock
                start_t = clock()
                results = \
                    iterative_deepening_search(state, expanded_state, evaluate,
                                               search, max_depth)
                runtime = clock() - start_t
                self._results = (results, runtime)

            def result(self):
                return self._results

        thread = MyThread()
        thread.start()
        print("Deciding on a move.", end='', flush=True)
        while thread.is_alive():
            sleep(1)
            # print(".", end='', flush=True)
        print('', flush=True)
        thread.join()
        (utility, move), time = thread.result()
        print("After", time, "seconds, the chosen move is:",
              string_position(move[0]) + string_position(move[1]))
        print("Move utility:", utility)
        return move, time, utility


def play_ply(state, expanded_state, for_human, pause_for, move_number,
             evaluate, search, max_depth):
    """
    Executes a full game ply either for a human player or for the AI. Returns
    True iff the game has reached a terminal state as a result of the ply.
    Records move data if the move is made by the AI.

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
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :return: True iff the game has reached a terminal state
    :rtype: bool
    """

    draw_board(state, move_number)
    move, time, _ = next_move(state, expanded_state, for_human, evaluate,
                              search, max_depth)
    if time is not None:  # Move was made by the AI.
        record_move_data(search, evaluate, max_depth, move_number,
                         player_turn(state), time)
    sleep(pause_for)
    move_piece(state, expanded_state, *move)
    print('')
    print('')
    terminal, utility = is_terminal(state, expanded_state)
    if terminal:
        draw_board(state, move_number, terminal, utility)
        print("Thanks for playing!")
    return terminal


def play(player_2_is_human, player_1_is_human, evaluate, search, max_depth,
         pause_for=0, gui_mode=False):
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
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param pause_for: number of seconds to pause for after getting the move
        from the human player or the AI before actually making the move;
        defaults to 0
    :type pause_for: int or float
    :param gui_mode: should the game be played in gui mode? defaults to False
    :type gui_mode: bool
    """
    move_number, state, expanded_state = setup_game()
    if not gui_mode:
        while True:
            if move_number == 51:
                exit()
            if play_ply(state, expanded_state, player_2_is_human, pause_for,
                        move_number, evaluate, search, max_depth):
                break
            if play_ply(state, expanded_state, player_1_is_human, pause_for,
                        move_number, evaluate, search, max_depth):
                break
            move_number += 1
    else:
        from gui import GameGUI
        GameGUI(evaluate, search, max_depth, player_1_is_human,
                player_2_is_human)


def play_single_player(evaluate, search, max_depth, gui_mode=False):
    """
    A game loop that has a human player playing interactively against the AI.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param gui_mode: should the game be played in gui mode? defaults to False
    :type gui_mode: bool
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
         max_depth, gui_mode=gui_mode)


def play_two_player(evaluate, search, max_depth, gui_mode=False):
    """
    A game loop that has a two human players playing against each other.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param gui_mode: should the game be played in gui mode? defaults to False
    :type gui_mode: bool
    """
    print('')
    play(True, True, evaluate, search, max_depth, gui_mode=gui_mode)


def play_ai_only(evaluate, search, max_depth, gui_mode=False):
    """
    A game loop that has the AI playing against itself, and displaying the
    game to onlookers.

    :param evaluate: a function taking a state and an expanded state and
        returning a heuristic estimate of the state's utility for the current
        player
    :type evaluate: (array of bytes, dict(byte, char)) => numeric
    :param search: a search function taking a state, an expanded state, an
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    :param gui_mode: should the game be played in gui mode? defaults to False
    :type gui_mode: bool
    """
    while True:
        # pause_for = input("How long to pause between moves? [non-negative] ")
        try:
            pause_for = float(0)
            if pause_for < 0:
                print("Invalid duration:", pause_for)
            else:
                break
        except ValueError:
            print("Invalid duration: '" + pause_for + "'")
    print('')
    play(False, False, evaluate, search, max_depth, pause_for, gui_mode)


def parse_positive_int(value):
    """
    Returns the integer value of the given string, raising an error if the
    string cannot be parsed to an integer, or if the resulting integer is not
    positive.

    :param value: the string to parse
    :type value: string
    :return: the integer value of the given string
    :rtype: int
    """
    pos = int(value)
    if pos < 1:
        raise argparse.ArgumentTypeError("invalid value: " + value)
    return pos


if __name__ == "__main__":
    # Define command line arguments.
    _parser = argparse.ArgumentParser(description="Play 'The Mad King! game.")
    _parser.add_argument("-e", "--eval", default=defaults['eval_name'],
                         choices=defaults['eval'].keys(),
                         help="the evaluation function to use")
    _parser.add_argument("-a", "--algorithm", default=defaults['search_name'],
                         choices=defaults['search'].keys(),
                         help="the search algorithm to use")
    _parser.add_argument("-d", "--depth", type=parse_positive_int,
                         default=defaults['depth'],
                         help="the depth limit of the search")
    _parser.add_argument("-r", "--replace", default=defaults['replace_name'],
                         choices=defaults['replace'].keys(),
                         help="the replacement policy to use")
    _parser.add_argument("-s", "--table-size", type=parse_positive_int,
                         default=defaults['table-size'],
                         help="the size of the transposition table")
    _parser.add_argument("-t", "--run-quick-test", action='store_true',
                         help="run a quick minimax/alpha-beta test instead of"
                              "playing the actual game")
    _parser.add_argument("-o", "--move-ordering", action='store_true',
                         help="use the move-ordered version of the successor"
                              "function")
    _parser.add_argument("-g", "--gui-mode", action='store_true',
                         help="Start game in GUI mode")

    # Parse command line arguments.
    _args = _parser.parse_args()
    _evaluate = defaults['eval'][_args.eval]
    _ordered = _args.move_ordering
    _gui_mode = _args.gui_mode
    search_alg = _args.algorithm
    if _args.move_ordering:
        _search = defaults['ordered-search'][search_alg]
    else:
        _search = defaults['search'][search_alg]
    _depth = _args.depth
    _replacement = defaults['replace'][_args.replace]
    _table_size = _args.table_size
    _run_quick_test = _args.run_quick_test

    # Initialize the global transposition table.
    init_table(_table_size, _replacement)

    if _run_quick_test:  # Run a search, and print results to console and file.
        print("Running", _args.algorithm, "with a depth limit of", _depth,
              "and a table of size", _table_size, "with policy", _args.replace,
              "with move ordering", _ordered)
        game_state = get_default_game_start()
        game_expanded_state = create_expanded_state_representation(game_state)
        result = _search(game_state, game_expanded_state, simple_eval, _depth)
        is_ordered = ""
        if _ordered:
            is_ordered = ".ordered"
        filename = _args.algorithm + ".depth" + str(_depth) + ".table_size" + \
            str(_table_size) + "." + _args.replace + is_ordered + ".json"
        dump_table(filename)
        print_utility_move_and_global_counters(result)
    else:  # Play the game.
        print("Welcome to madking!")
        print("We hope you have fun playing 'The Mad King!' game!")
        print('')
        # mode ='a'
        while True:
            mode = input("Single Player, Two Player, or AI Only Mode? [s/t/a] ")
            if mode in ["s", "t", "a"]:
                break
            print("Invalid choice: '" + mode + "'")
        if mode == "s":
            play_single_player(_evaluate, _search, _depth, _gui_mode)
        elif mode == "t":
            play_two_player(_evaluate, _search, _depth, _gui_mode)
        else:
            play_ai_only(_evaluate, _search, _depth, _gui_mode)
