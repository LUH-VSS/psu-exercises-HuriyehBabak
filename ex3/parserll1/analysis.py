from typing import Optional, Set

from parserll1.grammar import Grammar, Terminal, NonTerminal, Symbol, Word, Epsilon, isWord, Rule


class LL1Analysis:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar

    def EPS(self, word: Word, visited: Optional[Set[NonTerminal]] = None) -> bool:
        """
        Returns true if all non-terminals within word can result
        in the empty word via their derivations.
        """
        assert isWord(word), "{} must be a word".format(word)

        return False  # just placeholder

    def FIRST(self, word: Word, visited: Optional[Set[NonTerminal]] = None) -> Set[Terminal]:
        """
        Returns the FIRST set of word.

        The FIRST set contains all terminals which occur first at the right side of a derivation
        of a given non-terminal.
        """
        assert isWord(word), "{} must be a word".format(word)

        return set()  # just placeholder

    def FOLLOW(self, symbol: NonTerminal, visited: Optional[Set[NonTerminal]] = None) -> Set[Terminal]:
        """
        Returns the FOLLOW set of symbol.

        The FOLLOW set contains all terminals which occur right after the given non-terminal symbol
        when derivating from the start symbol S.
        """
        assert isinstance(symbol, NonTerminal), "{} must be a NonTerminal".format(symbol)

        return set()  # just placeholder

    def PREDICT(self, rule: Rule) -> Set[Terminal]:
        """
        Returns the PREDICT set of a given rule (A -> a) where
        A is a non-terminal and a is an arbitrary word of that grammar.

        The PREDICT set contains at least the FIRST set of the word a.
        If a, however, can become the empty word via derivation then
        the PREDICT set also contains the FOLLOW set of the non-terminal A.
        """
        assert isinstance(rule, Rule), "{} must be a rule".format(rule)

        return set()  # just placeholder
