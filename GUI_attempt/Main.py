import sys
sys.path.append('../')
import argparse
from minimax import *
from time import sleep
from evaluations import simple_eval, split_weight_eval
from search import iterative_deepening_search
from TranspositionTable import TranspositionTable
from state import string_position
state = None
expanded_state = None
move_number = 1
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
        return move, utility, time


def play_ply(state, expanded_state, for_human, pause_for, move_number,
             evaluate, search, max_depth):
    
    move, utility, time = next_move(state, expanded_state, for_human,
                                        evaluate, search, max_depth)  
    return string_position(move[0]) + string_position(move[1]), utility, time
    


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



