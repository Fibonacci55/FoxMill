from collections import UserDict



class Graph(UserDict):

    def __init__(self):
        UserDict .__init__(self)

    def add_node (self, node, attributes={}):
        self.data[node] = {'neighbours': list(), 'attributes' : attributes}
        #print (self.data)

    def add_edge (self, from_node, to_node):

        to_l = self.data[to_node]['neighbours']
        from_l = self.data[from_node]['neighbours']

        if from_node not in to_l:
            to_l.append (from_node)
        if to_node not in from_l:
            from_l.append (to_node)

        #print (self.data)

    def has_edge (self, from_node, to_node):
        print (from_node)
        return to_node in self.data[from_node]['neighbours'] and \
               from_node in self.data[to_node]['neighbours']

    def neighbours (self, of_node):
        pass
        res = [n for n in self.data[of_node]['neighbours']]
        return res


    def set_attribute (self, of_node, to):

        assert isinstance(to, dict())
        self.data[of_node]['attributes'] = to

    def get_attribute (self, of_node):
        return self.data[of_node]['attributes']

    def has_attribute (self, v, predicate=lambda x: True):
        #print ("has_attribute", v)
        return predicate(self.data[v]['attributes'])

    def enumerate (self, predicate=lambda x: True):

        for k, v in self.data.items():
            if predicate(v['attributes']):
                yield k
            #print (d[], type(d))
            #yield d
            #if predicate(d['attributes']):
            #    yield d


class x:

    def __init__(self, k):
        self.k = k


if __name__ == '__main__':

    g = Graph()

    x1 = x(2)
    x2 = x('sss')

    d = {}
    d[x1] = 3

    g.add_node (x1)
    g.add_node (x2)
    g.add_node ('bla')

    g.add_edge (x1, x2)
    g.add_edge ('bla', x2)
    print (g)
    print (g.has_edge (x1, x2))

    g.enumerate (predicate=lambda x: type(x) == type(''))
    for n in g.enumerate (lambda x: type(x) == type('')):
        print (n)