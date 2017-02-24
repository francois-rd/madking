import sys
sys.path.append('../')
import argparse
from minimax import *
from time import sleep
from evaluations import simple_eval, split_weight_eval
from search import iterative_deepening_search
from TranspositionTable import TranspositionTable
from state import string_position
state = get_default_game_start()
expanded_state = create_expanded_state_representation(state)
move_number = 1
moves = []
defaults = {
    'eval': {
        'simple': simple_eval,
        'split': split_weight_eval
    },
    'eval_name': 'simple',
    'search': {
        'minimax': minimax,
        'alpha-beta': alpha_beta
    },
    'search_name': 'minimax',
    'depth': DEFAULT_DEPTH_LIMIT,
    'replace': {
        'overall-oldest': TranspositionTable.replace_overall_oldest,
        'older-else-overall-oldest':
            TranspositionTable.replace_older_value_or_else_overall_oldest,
        'older-else-new':
            TranspositionTable.replace_older_value_or_else_new_entry,
        'shallower-else-some-shallower':
            TranspositionTable.replace_shallower_value_or_else_some_shallower,
        'shallower-else-overall-oldest':
            TranspositionTable.replace_shallower_value_or_else_overall_oldest,
        'shallower-else-new':
            TranspositionTable.replace_shallower_value_or_else_new_entry,
        'smaller-else-some-smaller':
            TranspositionTable.replace_smaller_subtree_or_else_some_smaller,
        'smaller-else-overall-oldest':
            TranspositionTable.replace_smaller_subtree_or_else_overall_oldest,
        'smaller-else-new':
            TranspositionTable.replace_smaller_subtree_or_else_new_entry,
        'two-deep': TranspositionTable.replace_two_deep,
        'two-big': TranspositionTable.replace_two_big
    },
    'replace_name': 'overall-oldest',
    'table-size': 1000000
}

def next_move(state, expanded_state, from_human, evaluate, search, max_depth):

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
                results = iterative_deepening_search(state, expanded_state, evaluate, search, max_depth)
                runtime = clock() - start_t
                self._results = (results, runtime)

            def result(self):
                return self._results

        thread = MyThread()
        thread.start()
        while thread.is_alive():
            pass
        thread.join()
        (utility, move), time = thread.result()
        return move


def play_ply(state, expanded_state, for_human, pause_for, move_number,
             evaluate, search, max_depth):
    
    from_tile_idx, to_tile_idx = next_move(state, expanded_state, for_human,
                                        evaluate, search, max_depth)  
    terminal, utility = is_terminal(state, expanded_state)
    return terminal, string_position(from_tile_idx) + string_position(to_tile_idx)
    


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
    """
    # move_number, state, expanded_state = setup_game()
    global expanded_state, state, move_number
    while True:
        if play_ply(state, expanded_state, player_2_is_human, pause_for,
                    move_number, evaluate, search, max_depth):
            break
        if play_ply(state, expanded_state, player_1_is_human, pause_for,
                    move_number, evaluate, search, max_depth):
            break
        move_number += 1


def play_single_player(evaluate, search, max_depth):
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
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    """
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
        evaluation function, a remaining depth, and returning a
        (<utility>, <move>) pair
    :type search: (array of bytes,
                   dict(byte, char),
                   (array of bytes, dict(byte, char)) => numeric,
                   int) => (numeric, (byte, byte))
    :param max_depth: the maximum search depth; must be at least 1
    :type max_depth: int
    """
    init_table(defaults["table-size"],defaults['replace_name'] )
    # play(False, False, evaluate, search, max_depth, 1)
    

    