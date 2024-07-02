class Epsilon:
    def __repr__(self):
        return "E"


class Terminal:
    def __init__(self, name, regex=None, skip=False, eof=False):
        self.name = name
        self.regex = regex
        self.skip = skip
        self.eof = eof

    def __repr__(self):
        return "T({})".format(self.name)


class NonTerminal:
    def __init__(self, name):
        self.name = name
        self.rules = []

    def __repr__(self):
        return "NT({})".format(self.name)


# Instead of defining an own type for Word, we use normal Python lists for this
def isSymbol(symbol):
    return isinstance(symbol, (Terminal, NonTerminal, Epsilon))


def isWord(word):
    if not isinstance(word, list):
        return False
    return all([isSymbol(s) for s in word])


class Rule:
    def __init__(self, lhs, rhs, action=None):
        assert isinstance(lhs, NonTerminal), "Left-hand side must be a non-terminal: {}".format(lhs)
        assert isWord(rhs), "Righ-hand side must be a word: {}".format(rhs)

        self.lhs = lhs
        self.rhs = rhs
        self.action = action

    def __repr__(self, ident=""):
        return "{0:{1}} -> {2}".format(repr(self.lhs), ident, self.rhs)


class Grammar:
    def __init__(self):
        self.terminals = {}
        self.nonterminals = {}
        self.rules = []
        self.start_symbol = None
        self.E = Epsilon()
        self.imports = {}

    def T(self, name, regex=None, skip=False):
        """Return the terminal with the given name. Create it, if it does not
        exist. The regex parameter is used by the scanner to detect
        the token from the character stream.

        """
        if name not in self.terminals:
            assert regex is not None, "Cannot create terminal {} without a regular expression.".format(name)
            self.terminals[name] = Terminal(name, regex=regex, skip=skip)
        else:
            assert regex is None, "Cannot re-initialize terminal {}.".format(name)

        return self.terminals[name]

    def NT(self, name, start=False):
        """Return the non-terminal with the given name. Create it, if it does not
        exist.
        """
        if name not in self.nonterminals:
            self.nonterminals[name] = NonTerminal(name)
        NT = self.nonterminals[name]
        if start:
            assert not (self.start_symbol), (
                "The grammar already defined the following start symbol: {}.\n"
                "Did you define multiple start symbols within your grammar?".format(self.start_symbol)
            )
            self.start_symbol = NT
        return NT

    def addRule(self, lhs, rhs, action=None):
        assert self.start_symbol, "Must define a start symbol, before you can add an rule to the grammar"
        rule = Rule(lhs, rhs, action)
        assert lhs in self.nonterminals.values(), (
            "{} hasn't been registered as non-terminal which is a necessity."
            "Please add it as non-terminal first.".format(lhs)
        )
        lhs.rules.append(rule)
        self.rules.append(rule)

    def addImport(self, name, module):
        self.imports[name] = module

    def pretty_print(self):
        print("Start symbol: {}".format(self.start_symbol))
        print("Terminals:    {}".format(list(self.terminals.keys())))
        print("NonTerminals: {}".format(list(self.nonterminals.keys())))
        print("Imports: {}".format(self.imports))
        print("Rules:")
        max_len_nonterminal = max([len(NT.name) for NT in self.nonterminals.values()])
        for r in self.rules:
            print(" ", r.__repr__(ident=max_len_nonterminal + 4))
