import sys
sys.path.append('../')
from state import *
from Pieces import *
board_width_pixels = 5
board_width_pixels = 5
state = get_default_game_start()
expanded_state = create_expanded_state_representation(state)
s_move = 14
e_move = 12
taking_input = False
inc = 0
piece = ""
s_pos = 0
e_pos = 0
moves = ['C2C3', 'D4E4','E2E3', 'C5D5']
def setup():
    size(255,255)
    global piece, moves, s_pos, e_pos
    moves.reverse()
    move = moves.pop()
    s_pos = tile_index(move[0:2])
    e_pos = tile_index(move[2:4])
    piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1] )
    
    
    

def draw():
    global state, expanded_state, inc, s_pos, e_pos, taking_input, piece
    draw_empty_board()
    draw_pieces(state, expanded_state, s_pos)
    if draw_board_with_animation(state, expanded_state, piece, e_pos):
        move_piece(state, expanded_state, s_pos, e_pos)  
        if len(moves) > 0:
            move = moves.pop()
            s_pos = tile_index(move[0:2])
            e_pos = tile_index(move[2:4])
            if (s_pos, e_pos) not in all_valid_moves(state, expanded_state):
                textSize(20);
                text("invalid  move(" +  str(s_pos) +" ," + str(e_pos) +")", 0, 120)
                text("Stopping the simulation", 0, 130)
                noLoop()  
            piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1] )

        
        
    
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
        move(state, expand_state, from_tile_index,
             end_tile_index)
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
        if num > 100:
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

    
    
def number_to_coordinate(n):
    return (n//5)*50, ((4-n)%5)*50

    