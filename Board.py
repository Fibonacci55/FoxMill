#import abc


import graph
import copy
import operator
from alphabeta import play_game, alphabeta_player

import logging

from stones import *
from move import *


class Position(object):
    def __init__(self, pos):
        l = pos.split("_")
        self.ring = l[0]
        self.pos = int(l[1])

    def __str__(self):
        return "%s_%s" % (self.ring, self.pos)

    def __repr__(self):
        return "%s_%s" % (self.ring, self.pos)


class Board(graph.Graph):
    empty = dict(stone=None)

    def __init__(self):

        graph.Graph.__init__(self)

        self.rings = ["Outer", "Middle", "Inner"]
        self.m = "Midpoint"
        self.empty = dict(stone=None)

        size = 10

        # Create Nodes
        for s in self.rings:
            for i in range(0, size):
                #
                #print "%s_%s" % (s,i%size), "%s_%s" % (s,(i+1)%size)
                self.add_node(("%s_%s" % (s, i % size)), attributes=self.empty)

        self.add_node(self.m, attributes=self.empty)

        # Create Rings
        for s in self.rings:
            for i in range(0, size):
                #
                #print "%s_%s" % (s,i%size), "%s_%s" % (s,(i+1)%size)
                self.add_edge("%s_%s" % (s, i % size), "%s_%s" % (s, (i + 1) % size))

        # Connect Rings
        for i in [i for i in range(0, size) if (i % 2) == 1]:
            #print ("%s_%s" % (self.rings[0], i % size), "%s_%s" % (self.rings[1], i % size))
            self.add_edge("%s_%s" % (self.rings[0], i % size), "%s_%s" % (self.rings[1], i % size))
            self.add_edge("%s_%s" % (self.rings[1], i % size), "%s_%s" % (self.rings[2], i % size))

        # Connect Midpoint
        for i in [i for i in range(0, size) if (i % 2) == 0]:
            #print ("%s_%s" % (self.rings[2], i % size), self.M)
            self.add_edge("%s_%s" % (self.rings[2], i % size), self.m)

            #

    def set(self, position, to):
        """

        @param position: Position on Board
        @param to: Stone or empty
        """
        assert isinstance(to, Stone)
        assert isinstance(position, Position)

        self.data[repr(position)]['attributes'] = to

    def remove(self, from_pos):
        assert self.data[from_pos]['attributes'] != empty
        self.data[from_pos]['attributes'] = empty


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        "Return a list of the allowable moves at this point."
        pass

    def result(self, state, move):
        "Return the state that results from making a move from a state."
        pass

    def utility(self, state, player):
        "Return the value of this final state to player."
        pass

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        return not self.actions(state)

    def to_move(self, state):
        "Return the player whose move it is in this state."
        return state.to_move

    def display(self, state):
        "Print or otherwise display the state."
        print(state)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


def node(ring, num):
    _node = "%s_%s" % (ring, num)
    return _node


class FoxMill(Game):
    def __init__(self, players=None):
        """
        :type self: object
        """
        self.board = Board()

        self.number_stones = 11
        self.number_foxes = 1
        self.number_blockers = 1

        self.players = players
        self.nplayer = 1
        self.current_player = Color.blue
        self.other_player = Color.red
        self.board = Board()

        self.size = 10

        self.available_simple_stones = {}
        self.available_foxes = {}
        self.available_blockers = {}
        self.removed_stones = {}

        for c in Color:
            self.available_simple_stones[c] = self.number_stones  #[SimpleStone(c) for i in range(0, self.size)]
            self.available_foxes[c] = self.number_foxes
            self.available_blockers[c] = self.number_blockers
            self.removed_stones[c] = []

        self.player = [Color.red, Color.blue]

        self.mod_size = lambda x: operator.imod(x, self.size)
        self.ml = lambda s, x, y, z: ["%s_%s" % (s, i) for i in map(self.mod_size, [x, y, z])]
        self.same_col = lambda a, b: a.color == b.color
        self.occupied = lambda x: x != Board.empty
        self.stones_of_same_player = lambda a, b: self.occupied(a) and self.occupied(b) and self.same_col(a, b)

    def switch_player(self):

        self.current_player, self.other_player = self.other_player, self.current_player

    def enumerate_set_possibilities(self, player):

        logging.debug("In _enumerate_SET_possibilities")
        possibilities = [p for p in self.board.enumerate(lambda x: x == self.board.empty)]
        if self.available_simple_stones[player] > 0:
            res = [SetStone(Position(p), SimpleStone(color=player)) for p in possibilities]
        if self.available_foxes > 0:
            res += [SetStone(Position(p), Fox(color=player)) for p in possibilities]
        if self.available_blockers > 0:
            res += [SetStone(Position(p), Blocker(color=player)) for p in possibilities]
        logging.debug(res)
        return res

    def enumerate_move_possibilities(self, player):
        """

        @param player:
        @return: List of empty positions on board
        """
        logging.debug("In _enumerate_MOVE_possibilities for player %s", player)
        occupied_by_player = lambda x: isinstance(x, Stone) and x.color == player
        res = []
        for pos in self.board.enumerate(occupied_by_player):
            #print ("Neighbours: ", str(pos), " ", self.board.neighbours(pos))
            for n in self.board.neighbours(pos):
                if self.board.has_attribute(n, lambda x: x == self.board.empty):
                    res.append(ShiftStone(pos, n, self.board.data[pos]['attributes']))
        return res

    def would_close_mill(self, move):
        occupied = lambda x: (isinstance(x, Stone) and x.color == self.current_player) or \
                             (isinstance(x, Blocker))
        occupied_other = lambda x: (isinstance(x, Stone) and x.color == self.other_player) or \
                                   (isinstance(x, Blocker))
        is_fox = lambda x: isinstance(x, Fox)
        p = move.to_pos.pos
        r = move.to_pos.ring
        s = move.stone
        #
        # "Normal" mill: Three stones of same color in a row
        # "FoxMill": Cornerstones with same number must be occupied
        #            by a fox and a stone of each color
        # "BlockerMill": A Blocker has no color and may therefore be used
        #                as stone (maybe not necessary to distinguish?)

        i = self.board.rings.index(r)
        rp = self.board.rings[(i + 1) % len(self.board.rings)]
        rm = self.board.rings[(i - 1) % len(self.board.rings)]

        if p % 2 == 0:
            # wie in is_mill nur die zwei "anderen" Steine checken.
            normal_mill = any([all([occupied(self.board.get_attribute(node(r, (p + 1) % self.size))),
                                    occupied(self.board.get_attribute(node(r, (p + 2) % self.size)))]),
                               all([occupied(self.board.get_attribute(node(r, (p - 1) % self.size))),
                                    occupied(self.board.get_attribute(node(r, (p - 2) % self.size)))])])
            fox_mill = all([any([occupied_other(self.board.get_attribute(node(rp, p))),
                                 occupied_other(self.board.get_attribute(node(rm, p)))]),
                            any([is_fox(s),
                                 is_fox(self.board.get_attribute(node(rp, p))),
                                 is_fox(self.board.get_attribute(node(rm, p)))]),
                            any([occupied(self.board.get_attribute(node(rp, p))),
                                 occupied(self.board.get_attribute(node(rm, p)))])])
            return normal_mill or fox_mill

        else:
            return any([all([occupied(self.board.get_attribute(node(r, (p + 1) % self.size))),
                             occupied(self.board.get_attribute(node(r, (p - 1) % self.size)))]),
                        all([occupied(self.board.get_attribute(node(rp, p))),
                             occupied(self.board.get_attribute(node(rm, p)))])])


    def is_mill(self, pos_triple, color):
        """

        @param pos_triple: Three positions on board, which may form a mill
        @param color: color for which to check (all three positions on
        board must be occupied by stones with the same color)
        """
        pass

    def in_mill(self, pos):

        """

        @param pos: Position (Ring/Number)
        @return: True/False
        """

        p = pos.pos

        print("Check for ", str(pos))

        print("p", p, type(p))
        if p % 2 == 0:
            to_check = [self.ml(pos.ring, p - 2, p - 1, p)] + [self.ml(pos.ring, p, p + 1, p + 2)]
            print("To Check / p == 0 % 2", to_check)
        else:
            to_check = [["%s_%s" % (s, p) for s in self.board.rings]] + [self.ml(pos.ring, p - 1, p, p + 1)]

        stone = self.board.get_attribute(str(pos))
        check_stone = lambda x: self.stones_of_same_player(stone, self.board.get_attribute(str(x)))
        print("=== End Check %s ==" % str(pos))
        return any([all(map(check_stone, l)) for l in to_check])

    def enumerate_remove_possibilities(self, player):
        pass
        all_stones_of_color = lambda x: isinstance(x, Stone) and x.color == player

        all_stones = [n for n in self.board.enumerate(all_stones_of_color)]
        res = [n for n in all_stones if not self.in_mill(Position(n))]
        if len(res) == 0:
            res = all_stones
        #res = [n for n in self.board.enumerate(all_stones_of_color)]
        print("Result", res)
        #res = self.board.enumerate(all_stones_of_color)
        return res


    def expand_move(self):
        # erweitern -> Wenn Mühle, einen entfernen
        # Fressen? Simple Move, Complex Move als Klassen
        # Nein: EIn Zug muss vollständig sein. D.h. man
        # muss das Schließen der Mühle und das Entfernen
        # eines Steines als einen Zug darstelleb!
        pass


    def actions(self):
        "Return a list of the allowable moves at this point."
        allowable_moves = self.enumerate_set_possibilities() + \
                          self.enumerate_move_possibilities()
        moves = []
        for m in allowable_moves:
            if self.would_close_mill(m):
                for r in self.enumerate_remove_possibilities(self.current_player):
                    moves.append(CloseMill(m, r))
            else:
                moves.append(m)
        return moves

    def result(self, state, move):
        new_game = copy.deepcopy(self)
        move(new_game)
        return new_game


    def utility(self, state, player):
        "Return the value of this final state to player."
        pass

    def terminal_test(self, state):
        "Return True if this is a final state for the game."
        return not self.actions(state)

    def to_move(self, state):
        "Return the player whose move it is in this state."
        return state.to_move

    def display(self, state):
        "Print or otherwise display the state."
        print(state)

    def set(self, pos, to):
        #node = "%s_%s" % (pos.ring, pos.pos)
        _node = node(pos.ring, pos.pos)

    def move(self, from_pos, to_pos):
        from_node = node(from_pos.ring, from_pos.pos)

        to_node = node(to_pos.ring, to_pos.pos)
        self.set(to_pos)

    def _may_close_mill(self, player):
        """

        @param player: Active player (red or blue)
        """
        pass



if __name__ == "__main__":
    logging.basicConfig(filename='Foxmill.log', level=logging.DEBUG)
    #players = [1, 2]
    b = Board()
    b.set(Position("Middle_3"), Stone(Color.red, StoneType.simple))
    b.set(Position("Middle_4"), Stone(Color.red, StoneType.simple))

    red = lambda x: isinstance(x, Stone) and x.color == Color.red
    blue = lambda x: isinstance(x, Stone) and x.color == Color.blue
    empty = lambda x: not isinstance(x, Stone)

    b1 = copy.deepcopy(b)
    b1.set(Position("Middle_5"), Stone(Color.red, StoneType.simple))

    print("\n ======= \n")

    #for k, v in b.data.items():
    #    print (k, v);
    #for s in b.enumerate (red):
    #    print (s)
    #print ("\n ======= \n")
    #for s in b1.enumerate (red):
    #    print (s)

    f = FoxMill()
    b = f.board
    b.set(Position("Middle_0"), Stone(Color.red, StoneType.simple))
    b.set(Position("Middle_1"), Stone(Color.red, StoneType.simple))
    b.set(Position("Middle_2"), Stone(Color.red, StoneType.simple))
    #print(f.in_mill(Position("Middle", 0)))
    #print(f.in_mill(Position("Outer", 0)))

    #l = f.enumerate_set_possibilities()
    #l.sort()
    #print (l)
    l = f.enumerate_move_possibilities(Color.red)
    print([str(i) for i in l])

    #b.set(Position("Inner", 0), Stone(Color.blue, StoneType.simple))
    #b.set(Position("Inner", 2), Stone(Color.blue, StoneType.simple))
    print("\n ======= \n")
    b.set(Position("Middle_2"), BlueSimple())
    #b.set(Position("Middle_0"), BlueSimple())
    #b.set(Position("Outer_0"), BlueSimple())
    b.set(Position("Outer_1"), BlueSimple())
    b.set(Position("Inner_1"), BlueSimple())
    #m = SetStone(Position("Outer_2"), BlueSimple())
    m = SetStone(Position("Middle_1"), BlueSimple())

    print("Would close Mill", f.would_close_mill(m))


    #b.set(Position("Outer_2"), BlueSimple())
    #l = f.enumerate_move_possibilities(Color.blue)
    #print ([str(i) for i in l])

    print("\n ======= \n")

    b.set(Position("Outer_2"), BlueSimple())
    b.set(Position("Middle_2"), Blocker(color=Color.red))
    m = SetStone(Position("Inner_2"), Fox(color=Color.red))
    print("Would close FoxMill", f.would_close_mill(m))

    #l = f.enumerate_remove_possibilities(Color.blue)
    #l.sort()
    #print ("Remove", [j for j in l])
    #print (f.enumerate_set_possibilities().sort())

    play_game(FoxMill(), alphabeta_player, alphabeta_player)
