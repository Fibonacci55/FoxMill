import abc

class base(abc.ABC):

    def __init__(self):
        super(base, self).__init__()

    def p(selfself):
        raise NotImplementedError


b = lambda x: x == 1

L = [[1,0,1],[1,0,1]]

m = lambda l: [i for i in map(b,l)]

if __name__ == '__main__':

    pass

    r = [m(l) for l in L]
    br = [all(i) for i in r]

    print(r, br)
    print (any(br))
    print (m(L[0]))