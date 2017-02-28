
from Main import *
import sys
sys.path.append('../')
from state import *
from Pieces import *
import copy
board_width_pixels = 5
board_width_pixels = 5
taking_input = False


player = { KING_PLAYER: "A", DRAGON_PLAYER :"H" }
evaluate = defaults['eval']["simple"]
algorithm = defaults['search']["alpha-beta"]
max_depth = defaults['depth']



s_move = 0
e_move = 0
piece = None
s_pos = 0
e_pos = 0
move = None
from_tile = 0
human_turn = True
from_turn = False
to_turn = False
game_started = True
paused = False
moves = []
cur = 0
temp_piece = None
s_temp_pos = 0
e_temp_pos = 0
temp_state = None
temp_expanded_state = None
switch_mode = ''
current_utility = ""
current_time = ""
temp_current_time = 0.0
temp_current_utility = 0.0



def start_game():
    global state, expanded_state, moves, current_utility, temp_current_time, temp_current_utility
    moves = []
    state = get_default_game_start()
    expanded_state = create_expanded_state_representation(state)
    draw_empty_board()
    draw_pieces(state, expanded_state, -1)
    init_table(defaults["table-size"],defaults['replace_name'])
    s_move = 0
    e_move = 0
    piece = None
    s_pos = 0
    e_pos = 0
    move = None
    from_tile = 0
    human_turn = True
    from_turn = False
    to_turn = False
    game_started = True
    paused = False
    moves = []
    cur = 0
    temp_piece = None
    s_temp_pos = 0
    e_temp_pos = 0
    temp_state = None
    temp_expanded_state = None
    switch_mode = ''
    current_utility = 0.0
    current_time = 0.0
    temp_current_time = 0.0
    temp_current_utility = 0.0





def setup():
    size(250,400)
    start_game()

def draw():
    if game_started and not paused:
        global state, expanded_state, inc, s_pos, e_pos, taking_input, piece, move, human_turn, evaluate, algorithm, max_depth
        global current_utility, current_time, temp_current_time, temp_utility_time
        draw_empty_board()
        draw_pieces(state, expanded_state, s_pos)
        text("Utility " + str(current_utility), 80, 275)
        text("Time " + str(current_time), 80, 295)
        if  player[player_turn(state)] == "A":
            if piece == None:
                    move, utility, time = play_ply(state, expanded_state, False, 1, 1, evaluate, algorithm, max_depth)
                    moves.append((move, utility, time))
                    current_utility = utility
                    current_time = time
                    s_pos = tile_index(move[0:2])
                    e_pos = tile_index(move[2:4])    
                    piece = Piece(expanded_state[s_pos], number_to_coordinate(s_pos)[0],number_to_coordinate(s_pos)[1])
            if draw_board_with_animation(state, expanded_state, piece, e_pos):
                    move_piece(state, expanded_state, s_pos, e_pos)
                    draw_pieces(state, expanded_state, s_pos)
                    check_win()                    
                    human_turn = True
                    piece = None
        if from_turn:
            draw_piece(expanded_state[from_tile], mouseX - 25, mouseY - 25)
    elif paused:
        global temp_expanded_state, temp_state, state, expanded_state, temp_piece, e_temp_pos
        global s_temp_pos, temp_current_utility, temp_current_time
        draw_empty_board()
        draw_pieces(temp_state, temp_expanded_state, s_temp_pos)
        text("Utility " + str(temp_current_utility), 80, 275)
        text("Time " + str(temp_current_time), 80, 295)
        if draw_board_with_animation(temp_state, temp_expanded_state, temp_piece, e_temp_pos):
            move_piece(temp_state, temp_expanded_state, s_temp_pos, e_temp_pos)
        pushStyle()
        textSize(30)
        text("PAUSED", 80, 125)
        popStyle()
        
        
        
        
        
    
def draw_board_with_animation(state,expand_state, mover, dest):
    if mover is not None:
        return mover.update(number_to_coordinate(dest)[0], number_to_coordinate(dest)[1]) 
    
    
    
def draw_empty_board():
    background(255,255,255)
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
    if game_started and not paused:
        global expanded_state, s_pos, from_tile, from_turn, to_turn, to_tile,human_turn
        global current_utility, current_time 
        if human_turn and player[player_turn(state)]=="H":
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
                        human_turn = True
                        move = string_position(from_tile)+ string_position(to_tile)
                        current_utility = "" 
                        current_time = ""
                        moves.append((move, current_utility, current_time))
                        move_piece(state, expanded_state, from_tile, to_tile)
                        check_win()
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
    
def keyPressed():
    global paused, temp_piece, piece, cur, e_temp_pos, s_temp_pos, s_pos, e_pos
    global temp_expanded_state, temp_state, state, expanded_state, switch_mode
    global current_time, current_utility, temp_current_time, temp_utility_time
    if key in ["r", "R"]:
        start_game()
        
    if key in ["p", "P"]:
        paused = not paused
        if paused:
            s_temp_pos = s_pos
            e_temp_pos = e_pos
            temp_piece = piece
            temp_state = copy.deepcopy(state)
            temp_expanded_state = copy.deepcopy(expanded_state)
            temp_current_time = current_time
            temp_utility_time = current_utility
            cur = len(moves) - 1
    if paused:
        if key in ["a", "A"]:
            if switch_mode != 'a':
                switch_mode = 'a'
            else:
                if cur >= 1:
                    cur -= 1
            move,temp_utility_time, temp_current_time  = moves[cur]
            e_temp_pos = tile_index(move[0:2])
            s_temp_pos = tile_index(move[2:4])   
        if key in ["d", "D"]:
            if switch_mode != 'd': 
                switch_mode = 'd'
            else:
                if cur < len(moves) - 1:
                    cur += 1

            move,temp_utility_time, temp_current_time  = moves[cur]
            print(temp_current_time)
            s_temp_pos = tile_index(move[0:2])
            e_temp_pos = tile_index(move[2:4])   

        temp_piece = Piece(temp_expanded_state[s_temp_pos], number_to_coordinate(s_temp_pos)[0],number_to_coordinate(s_temp_pos)[1])

def check_win():
    terminal, evaluation = is_terminal(state, expanded_state)
    if terminal:
        pushStyle()
        textSize(30)
        if evaluation == DRAGON_WIN:
            text("DRAGON WON", 80, 275)
        elif evaluation == KING_WIN:
            text("KING WON", 80, 275)
        else:
            text("DRAW", 80, 275)
        noLoop()
    


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