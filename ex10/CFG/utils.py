import logging


def functions_to_dot(functions, filename):
    logging.info(f"Dumping {len(functions)} function CFGs to {filename} as DOT")
    with open(filename, "w+") as fd:
        print("digraph G {  compound=true; graph [rankdir=TD]; node [shape=record];", file=fd)
        for idx, function in enumerate(functions):
            print(f'subgraph cluster{idx} {{ label="{function.label}"', file=fd)
            for bb in function.basic_blocks:
                ir = "\\l".join([repr(instr) for instr in bb.instructions]) + "\\l"
                text = f"{{ {bb.label} | {ir}}}"
                text = text.replace('"', "'")
                print(f' bb_{id(bb)}[shape=record,label="{text}"];', file=fd)
                for bb2 in bb.successors():
                    print(f" bb_{id(bb)} -> bb_{id(bb2)};", file=fd)
            print("}", file=fd)
        print("}", file=fd)


class EquivalenceClasses:
    """This class is kind of ugly. Therefore, I hide it from you in the
    utils class.

    This class manages sets of equivalent symbols. You can union two
    symbols to be equal, kill the equivalence between two symbols,
    query for the equivalent set and merge multiple instances of this
    class.

    This datastructure uses some kind of union-find datastructure. The
    self.data keys are all symbols that are know to the
    data-structure. If two keys are equivalent they have the _SAME_
    set as a mappping value. Thereby, the update mechanism is
    relatively easy and efficient.

    """

    def __init__(self, other=None):
        """If other is not None, copy the other EquivalenceClass object."""
        self.data = {}
        self.logger = logging.getLogger("ec")
        if other is None:
            return

        # Copy the unions from the other class
        for union in other.unions:
            union = union.copy()
            for elem in union:
                self.data[elem] = union

    @property
    def symbols(self):
        """All symbols that are mentioned in any set"""
        return list(self.data.keys())

    @property
    def unions(self):
        copy = self.data.copy()
        while copy:
            key, ec = copy.popitem()
            yield ec
            for other in [x for x in ec if x != key]:
                del copy[other]

    def find(self, a):
        """Returns a set that includes all elements that are equivalent to a"""
        if a in self.data:
            return self.data[a]
        return {a}

    def union(self, a, b):
        a_set = self.find(a)
        b_set = self.find(b)
        a_set.update(b_set)  # This is an in-place update!
        self.data[a] = a_set
        for elem in b_set:
            self.data[elem] = a_set
        # self.logger.debug(f"UNION {a}, {b}, equiv-sets: {self}")

    def kill(self, a):
        """Remove a from any equivalence set"""
        if a in self.data:
            a_set = self.data[a]
            del self.data[a]
            a_set.remove(a)
            if len(a_set) == 1:
                del self.data[a_set.pop()]
        # self.logger.debug(f"KILL {a} equiv-sets: {self}")

    @staticmethod
    def merge(many_equiv_classes):
        ret = EquivalenceClasses()
        # 1. Gather all symbols that occur in our sets
        symbols = set().union(*[x.symbols for x in many_equiv_classes])

        # 2. For every symbol, we find the intersection in all equivalence_classes
        while symbols:
            # 2.1 Get one symbol from the queue
            symbol = symbols.pop()
            # 2.2 Get all equivalence_sets from all classes
            sets = [equiv_class.find(symbol) for equiv_class in many_equiv_classes]

            # 2.3 Build the intersection.
            #
            # In equivalent, we will end up with all symbols that are
            # equivalent to symbol in all equivalent classes
            equivalent = set.intersection(*sets)
            if len(equivalent) > 1:  # Avoid the trivial equivalence
                for elem in equivalent:
                    ret.data[elem] = equivalent

            # 2.4 We already covered these
            symbols -= equivalent  # We have already covered these symbols

        # logging.getLogger("ec").debug(f"MERGE: {many_equiv_classes} -> {ret}")
        return ret

    def __eq__(self, other):
        for symbol in self.symbols:
            if self.find(symbol) != other.find(symbol):
                return False
        return True

    def __repr__(self):
        return f"<EQ {list(self.unions)}>"


if __name__ == "__main__":
    x = EquivalenceClasses()
    x.union(1, 2)
    x.union(2, 3)

    y = EquivalenceClasses()
    y.union(1, 2)

    z = EquivalenceClasses.merge([x, y])

    print(x, y, z)
