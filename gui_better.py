try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    simplegui.Frame._hide_status = True
    simplegui.Frame._keep_timers = False

import math
from state import *
import Main as m
game_gui = None
piece_color = {
    GUARD: '#FF5733',
    DRAGON: '#E12E2E',
    KING: '#539E36'
}

player_turn_gui = {
    KING_PLAYER: "A",
    DRAGON_PLAYER: "A",
}


def point_to_rec_coords(v, rect_size=100):
    def to_tuple(v, x=0, y=0):
        """
        Return the vector as a tuple.

        :return: (int or float, int or float)
        """
        return (v[0]+x, v[1]+y)

    l = []
    l.append(to_tuple(v, 0,rect_size))
    l.append(to_tuple(v))
    l.append(to_tuple(v, rect_size))
    l.append(to_tuple(v, rect_size, rect_size))
    return l


def get_rect_from_coordinates(x, y):
    xRect = math.floor(x/100)
    yRect = math.floor(y/100)
    return xRect*5 + (4-yRect)


def number_to_coordinate(n):
    return (n//5)*100, ((4-n)%5)*100


class Vector:
    """
    Vector (self.x, self.y).
    """
    def __init__(self, x, y):
        """
        Initialize the vector.

        :param x: int or float
        :param y: int or float
        """
        assert isinstance(x, int) or isinstance(x, float)
        assert isinstance(y, int) or isinstance(y, float)

        self.x = x
        self.y = y

    def add(self, other):
        """
        Adds other to self.

        :param other: Vector
        """
        assert isinstance(other, Vector)

        self.x += other.x
        self.y += other.y

    def sub(self, other):
        """
        Adds other to self.

        :param other: Vector
        """
        assert isinstance(other, Vector)

        self.x -= other.x
        self.y -= other.y

    def magnitude(self):
        return math.sqrt(self.x * self.x + self.y * self.y )


    def div(self, n):
        self.x = self.x/n
        self.y = self.y/n



    def normalize(self):
        m = self.magnitude()
        if m != 0 and m != 1:
            self.div(m)

    def limit(self, max):
        if self.magSq() > max*max:
            self.normalize()
            self.mul_scalar(max)


    def magSq(self):
        return (self.x * self.x + self.y * self.y)



    def mul_scalar(self, scalar):
        """
        Multiplies self by scalar.

        :param scalar: int or float
        """
        assert isinstance(scalar, int) or isinstance(scalar, float)

        self.x *= scalar
        self.y *= scalar

    def distance(self, other):
        """
        Return the distance between self and other.

        :param other: Vector

        :return: float >= 0
        """
        assert isinstance(other, Vector)

        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def same(self, other):
        """
        If (self.x, self.y) == (other.x, other.y)
        then return True,
        else return False.

        :param other: Vector
        """
        assert isinstance(other, Vector)

        return (self.x == other.x) and (self.y == other.y)

    def to_tuple(self, x=0, y=0):
        """
        Return the vector as a tuple.

        :return: (int or float, int or float)
        """
        return (self.x+x, self.y+y)

    def to_coordinates(self, rect_size=100):
        return point_to_rec_coords(self.to_tuple(), rect_size)


class Game_GUI:
    def __init__(self, evaluate, search, max_depth, player1_human, player2_human):
        global game_gui, player_turn_gui
        self.moves = []
        self.pieces = {}
        self.state = get_default_game_start()
        self.expanded_state = create_expanded_state_representation(self.state)
        self.evaluate = evaluate
        self.search = search
        self.max_depth = max_depth
        self.recalc_pieces()
        self.terminal = False
        self.utility = 0
        self.time = 0
        self.paused = False
        self.counter = -1
        game_gui = self
        player_turn_gui[KING_PLAYER] = "H" if player1_human else "A"
        player_turn_gui[DRAGON_PLAYER] = "H" if player2_human else "A"
        self.frame = simplegui.create_frame('Madking', 500, 500)
        self.ut_label = self.frame.add_label("Utility: " + str(self.utility))
        self.time_label = self.frame.add_label("Time: " + str(self.time))
        def pause_handle():
            self.paused = not self.paused
        self.frame.add_button("pause", pause_handle)
        self.frame.set_draw_handler(draw)
        self.frame.set_mouseclick_handler(mouse_pressed)
        self.frame.start()


    def update_utility(self, u):
        self.utility = u
        self.ut_label.set_text("Utility: " + str(self.utility))

    def update_time(self, t):
        self.time = t
        self.time_label.set_text("Time: " + str(self.time))

    def recalc_pieces(self):
        for i, num in get_live_pieces_enumeration_no_king(self.state):
            if num >= 100:
                num -= 100
            x, y = number_to_coordinate(num)
            self.pieces[num] = Piece(self.expanded_state[num], x, y, num)

        k_num = get_king_tile_index(self.state)
        x, y = number_to_coordinate(k_num)
        self.pieces[k_num] = Piece(KING, x, y, k_num)

    def add_move(self, move):
        self.moves.append(move)
        self.counter += 1


class Piece:
  selected = -1
  mouseX = -1
  mouseY = -1
  def __init__(self, type,x ,y, num):
      self.location =  Vector(x,y)
      self.velocity =  Vector(0,0)
      self.top_speed = 2000
      self.type = type
      self.num = num

  def update(self, canvas):
    if Piece.mouseX != -1:
        x = self.mouseX
        y = self.mouseY
        mouse = Vector(x,y)
        mouse.sub(self.location)
        if  mouse.magnitude() > 3:
            mouse.normalize()
            mouse.mul_scalar(10)
            acceleration = mouse
            self.location.add(acceleration)
            self.velocity.limit(self.top_speed)
            self.location.add(self.velocity)
        else:
            Piece.selected = -1
            self.location.x = x
            self.location.y = y
            Piece.mouseX = -1
            game_gui.recalc_pieces()

        self.display(canvas)


  def display(self,canvas):

      black = 255
      black = '#' + ('0' + hex(black)[-1] if black < 16
                     else hex(black)[-2:]) * 3

      if self.num != Piece.selected:
          canvas.draw_polygon(self.location.to_coordinates(), 1, piece_color[self.type], piece_color[self.type])
      else:
          color = 1
          color = '#' + ('0' + hex(color)[-1] if color < 16
                         else hex(color)[-2:]) * 3
          canvas.draw_polygon(self.location.to_coordinates(), 10,  color, piece_color[self.type])
      canvas.draw_text(self.type, self.location.to_tuple(40,50), 20,black)


def draw_empty_board(canvas):
    color = 255
    color = '#' + ('0' + hex(color)[-1] if color < 16
                   else hex(color)[-2:]) * 3

    black = 0
    black = '#' + ('0' + hex(black)[-1] if black < 16
                   else hex(black)[-2:]) * 3

    for i in range(BOARD_NUM_RANKS):
        for j in range(BOARD_NUM_FILES):
            tile_i = tile_index(chr(i+65)+str(j+1))
            x, y = number_to_coordinate(tile_i)
            canvas.draw_polygon(point_to_rec_coords((x, y)), 1, black, color)


def mouse_pressed(mouse):
    if Piece.mouseX == -1 and not game_gui.terminal:
        state = game_gui.state
        expanded_state = game_gui.expanded_state
        num = get_rect_from_coordinates(mouse[0],mouse[1])
        if player_turn_gui[player_turn(state)] == 'H':
            if Piece.selected == -1 and expanded_state[num] != '.':
                Piece.selected = num
                Piece.mouseX = -1
                Piece.mouseY = -1

            elif Piece.selected != -1:
                selected = Piece.selected
                if selected != num and (selected, num) in all_valid_moves(state, expanded_state):
                    game_gui.add_move((selected , num))
                    move_piece(game_gui.state, game_gui.expanded_state, selected , num)
                    Piece.mouseX, Piece.mouseY = number_to_coordinate(num)
                    Piece.selected = num
                    game_gui.pieces[num] = game_gui.pieces[selected]
                    game_gui.pieces[num].num = num
                    del game_gui.pieces[selected]
                    terminal, utility = is_terminal(game_gui.state,
                                                    game_gui.expanded_state)
                    game_gui.terminal = terminal
                    game_gui.utility = utility
                else:
                    Piece.selected = -1


def draw(canvas):
    """
    Event handler to draw all items.
    :param canvas: simplegui.Canvas
    """
    if not game_gui.paused:
        if not game_gui.terminal :
            if Piece.selected == -1 and player_turn_gui[player_turn(game_gui.state)] == 'A':
                ai_move, time, utility = m.next_move(game_gui.state, game_gui.expanded_state, False,
                                    game_gui.evaluate, game_gui.search, game_gui.max_depth)
                game_gui.update_utility(utility)
                game_gui.update_time(time)
                game_gui.add_move(ai_move)
                move_piece(game_gui.state, game_gui.expanded_state, ai_move[0], ai_move[1])
                Piece.mouseX, Piece.mouseY = number_to_coordinate(ai_move[1])
                Piece.selected = ai_move[1]
                game_gui.pieces[ai_move[1]] = game_gui.pieces[ai_move[0]]
                game_gui.pieces[ai_move[1]].num = ai_move[1]
                del game_gui.pieces[ai_move[0]]
                terminal, utility = is_terminal(game_gui.state, game_gui.expanded_state)
                game_gui.terminal = terminal
                game_gui.utility = utility

    draw_empty_board(canvas)
    for piece in game_gui.pieces.values():
        if Piece.mouseX != -1 and piece.num == Piece.selected:
            piece.update(canvas)
        piece.display(canvas)

    if game_gui.terminal:
        text = ""
        if game_gui.utility == DRAW:
            text = "DRAW"
        elif game_gui.utility == KING_WIN:
            text = "KING WON"
        elif game_gui.utility == DRAGON_WIN:
            text = "DRAGON WON"
        canvas.draw_text(text, (50,250), 30, "#000000")

