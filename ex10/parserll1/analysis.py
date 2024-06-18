from parserll1.grammar import Terminal, NonTerminal, Epsilon, isWord, Rule


class AnalysisError(RuntimeError):
    pass


class LL1Analysis:
    def __init__(self, grammar):
        self.grammar = grammar

    def EPS(self, word, visited=None):
        """
        Returns true if all non-terminals within word can result
        in the empty word via their derivations.
        """

    def FIRST(self, word, visited=None):
        """
        Returns the FIRST set of word.

        The FIRST set contains all terminals which occur first at the right side of a derivation
        of a given non-terminal.
        """

    def FOLLOW(self, symbol, visited=None):
        """
        Returns the FOLLOW set of symbol.

        The FOLLOW set contains all terminals which occur right after the given non-terminal symbol
        when derivating from the start symbol S.
        """

    def PREDICT(self, rule):
        """
        Returns the PREDICT set of a given rule (A -> a) where
        A is a non-terminal and a is an arbitrary word of that grammar.

        The PREDICT set contains at least the FIRST set of the word a.
        If a, however, can become the empty word via derivation then
        the PREDICT set also contains the FOLLOW set of the non-terminal A.
        """
