from enum import Enum


class Color(Enum):
    red = 1
    blue = 2


class StoneType(Enum):
    simple = 1
    fox = 2
    blocker = 3


class Stone(object):
    def __init__(self, color=Color.red, typ=StoneType.simple):
        self.color = color
        self.typ = typ

    def __str__(self):
        return "%s/%s" % (self.typ, self.color)

class SimpleStone (Stone):

    def __init__(self, color):
        super(SimpleStone, self).__init__(color=color, typ=StoneType.simple)
        #Stone.__init__(self,color=color, typ=StoneType.simple)

class BlueSimple(SimpleStone):

    def __init__(self):
        super(SimpleStone, self).__init__(color=Color.blue, typ=StoneType.simple)

class RedSimple(SimpleStone):

    def __init__(self):
        super(SimpleStone, self).__init__(color=Color.red, typ=StoneType.simple)


class Fox (Stone):

    def __init__(self, color):
        Stone.__init__(self, color=color, typ=StoneType.fox)


class Blocker (Stone):

    def __init__(self, color):
        Stone.__init__(self, color=color, typ=StoneType.blocker)
