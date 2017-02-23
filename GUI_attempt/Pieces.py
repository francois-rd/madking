king_color = color(0,255,0)
guard_color = color(0,125,125)
dragon_color = color(255,0,0)
class Piece:

  def __init__(self, type,x ,y):
    self.location =  PVector(x,y)
    self.velocity =  PVector(0,0)
    self.topspeed = 4
    self.type = type

  def update(self, x , y):
    b = False
    mouse = PVector(x,y)
    dir = PVector.sub(mouse,self.location)
    if dir.mag() > 1:
        dir.normalize()
        dir.mult(0.5) 
        acceleration = dir
        self.velocity.add(acceleration)
        self.velocity.limit(self.topspeed)
        self.location.add(self.velocity)
        b = False
    else:
        self.location.x = x
        self.location.y = y
        b = True
    self.checkEdges()
    self.display()
    return b

  def display(self):
    global dragon_color, guard_color, king_color
    stroke(0)
    if self.type == 'G':
        fill(guard_color)
    if self.type == 'D':
        fill(dragon_color)
    if self.type == 'K':
        fill(king_color)
    rect(self.location.x,self.location.y,50,50)
    fill(0)
    text(self.type, 24 + self.location.x,24 + self.location.y) 

  def checkEdges(self):
    if self.location.x > width:
      self.location.x = 0
    elif self.location.x < 0:
      self.location.x = width
    

    if self.location.y > height:
      self.location.y = 0;
    elif self.location.y < 0 :
      self.location.y = height
    

  
