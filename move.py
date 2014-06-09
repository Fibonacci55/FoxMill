class Move(object):

    def __init__(self, stone):
        self.stone = stone
        pass

    def __call__(self, board):
        assert (isinstance(board, FoxMill))
        pass


class SetStone(Move):

    def __init__(self, position, stone):
        Move.__init__(self, stone)
        self.to_pos = position

    def __call__(self, game):
        assert (isinstance(game, FoxMill))
        game.board.set(self.position, self.stone)


class ShiftStone(Move):

    def __init__(self, from_pos, to_pos, stone):
        super(ShiftStone, self).__init__(stone)
        self.from_pos = from_pos
        self.to_pos = to_pos


    def __call__(self, game):
        assert (isinstance(game, FoxMill))
        s = game.board.data[self.from_pos]['attributes']
        game.board.remove(self.from_pos)
        game.board.set(self.to_pos, s)

    def __str__(self):
        return "From %s To %s" % (str(self.from_pos), str(self.to_pos))


class RemoveStone(Move):

    def __init__(self, from_pos, stone):
        super(RemoveStone, self).__init__(stone)
        self.from_pos = from_pos

    def __call__(self, game):
        game.board.remove(self.from_pos)

    def __str__(self):
        return "Remove stone from %s" % self.from_pos


class CloseMill (Move):

    def __init__(self, move, remove):
        super(CloseMill, self).__init__()
        self.move = move
        self.remove = remove

    def __call__(self, game):
        pass
