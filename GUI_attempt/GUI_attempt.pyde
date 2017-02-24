from Main import *
import sys
sys.path.append('../')
from state import *
from Pieces import *
from threading import Thread
board_width_pixels = 5
board_width_pixels = 5
s_move = 0
e_move = 0
taking_input = False
inc = 0
piece = None
s_pos = 0
e_pos = 0
thread = None
move = None
from_tile = 0
human_turn = True
from_turn = False
to_turn = False



def setup():
    size(250,250)
    global piece, s_pos, e_pos
    draw_empty_board()
    draw_pieces(state, expanded_state, -1)
    
    init_table(defaults["table-size"],defaults['replace_name'] )
    if not human_turn:
        piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1])
        terminal, move = play_ply(state, expanded_state, False, 1, 1, defaults['eval']['simple'], defaults['search']['alpha-beta'], defaults['depth'])
        s_pos = tile_index(move[0:2])
        e_pos = tile_index(move[2:4])    
        piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1])


    
def draw():
    global state, expanded_state, inc, s_pos, e_pos, taking_input, piece, move, human_turn
    draw_empty_board()
    draw_pieces(state, expanded_state, s_pos)
    if not human_turn:
        if piece == None:
                terminal, move = play_ply(state, expanded_state, False, 1, 1, defaults['eval']['simple'], defaults['search']['alpha-beta'], defaults['depth'])
                s_pos = tile_index(move[0:2])
                e_pos = tile_index(move[2:4])    
                piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1])
        if draw_board_with_animation(state, expanded_state, piece, e_pos):
                move_piece(state, expanded_state, s_pos, e_pos)
                draw_pieces(state, expanded_state, s_pos)
                human_turn = True
                piece = None
                
                # terminal, move = play_ply(state, expanded_state, False, 1, 1, defaults['eval']['simple'], defaults['search']['alpha-beta'], defaults['depth'])
                # s_pos = tile_index(move[0:2])
                # e_pos = tile_index(move[2:4])    
                # piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1])
                # s_pos = -1
                
    if from_turn:
        draw_piece(expanded_state[from_tile], mouseX - 25, mouseY - 25)

        
        
    
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
    expand_state = expand_state_representation(state)
    draw_empty_board(state, expand_state)
    for m in moves:
        from_tile_index = tile_index(m[0:2])
        end_tile_index = tile_index(m[2:4])
        if not is_valid_move(expand_state, from_tile_index, end_tile_index):
            print("Bad happened at move " + m)
            print("Stopping the simulation")
            break
        # move(state, expand_state, from_tile_index,
        #      end_tile_index)
        draw_empty_board(state, expand_state)
        change_player_turn(state)
        terminal, status = is_terminal(state, expand_state)
        if terminal:
            print(status)
            break

def draw_board_with_animation(state,expand_state, mover, dest):
    return mover.update(number_to_coordinate(dest)[0], number_to_coordinate(dest)[1]) 
    
    
    
def draw_empty_board():
    visited = []
    global king_color, dragon_color, guard_color
    for i in range(BOARD_NUM_RANKS):
        for j in range(BOARD_NUM_FILES):
            tile_i = tile_index(chr(i+65)+str(j+1))
            x, y = number_to_coordinate(tile_i)
            fill(255)
            rect (x, y, 50, 50)
            fill(0)
            text( str(tile_i),x + 25, y + 25)

def draw_pieces(state, expanded_state, no_draw):
    for i, num in get_live_pieces_enumeration_no_king(state):
        if num >= 100:
            num-=100
        if no_draw != num:
            stored_piece = expanded_state[num]
            if  stored_piece != '.':
                if stored_piece == 'G':
                    fill(guard_color)
                if stored_piece == 'D':
                    fill(dragon_color)
                x, y = number_to_coordinate(num)
                rect (x, y , 50, 50)
                fill(0)
                text(stored_piece, 24 + x,24 + y) 

    k_tile = get_king_tile_index(state)
    if no_draw != k_tile:
        x, y = number_to_coordinate(k_tile)
        fill(king_color)
        rect (x,y, 50, 50)
        fill(0)
        text('K', 24 + x,24 + y) 



    

    
        
    
     
def mousePressed():
    global expanded_state, s_pos, from_tile, from_turn, to_turn, to_tile,human_turn 
    if human_turn:
        if not from_turn:
            x = mouseX
            y = mouseY
            from_tile = get_rect_from_coordinates(x ,y)
            if  expanded_state[from_tile] != '.':
                from_turn = True
                s_pos = from_tile
        else:
            if not to_turn:
                x = mouseX
                y = mouseY
                to_tile = get_rect_from_coordinates(x ,y)
                if (from_tile, to_tile) in all_valid_moves(state, expanded_state):
                    from_turn = False
                    true_turn = False
                    human_turn = False
                    move_piece(state, expanded_state, from_tile, to_tile)
                else:
                    from_turn = False
                    true_turn = False
                    s_pos = -1

                    
                    
                    
                
            
            
def draw_piece(type, tile_index):
    if type == 'G':
        fill(guard_color)
    if type == 'D':
        fill(dragon_color)
    if type == 'K':
        fill(king_color)
    x, y = number_to_coordinate(tile_index)
    rect (x, y , 50, 50)
    fill(0)
    text(type, 24 + x,24 + y)
    
      
def draw_piece(type, x, y):
    if type == 'G':
        fill(guard_color)
    if type == 'D':
        fill(dragon_color)
    if type == 'K':
        fill(king_color)
    rect (x, y , 50, 50)
    fill(0)
    text(type, 24 + x,24 + y) 
    
    
    
    
def get_rect_from_coordinates(x, y):
    xRect = x/50
    yRect = y/50
    return xRect*5 + (4-yRect)

def number_to_coordinate(n):
    return (n//5)*50, ((4-n)%5)*50