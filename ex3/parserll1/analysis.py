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
        assert isWord(word), "{} is no word".format(word)

        if not visited:
            visited = set()

        for symbol in word:
            if isinstance(symbol, Epsilon):
                continue
            elif isinstance(symbol, Terminal):
                return False
            elif isinstance(symbol, NonTerminal):
                if symbol in visited:
                    continue
                visited.add(symbol)
                if not any(self.EPS(rule.rhs, visited) for rule in symbol.rules):
                    return False

        return True

    def FIRST(self, word: Word, visited: Optional[Set[NonTerminal]] = None) -> Set[Terminal]:
        """
        Returns the FIRST set of word.

        The FIRST set contains all terminals which occur first at the right side of a derivation
        of a given non-terminal.
        """
        assert isWord(word), "{} is no word".format(word)

        first = set()

        if not visited:
            visited = set()

        for symbol in word:
            if isinstance(symbol, Epsilon):
                continue
            elif isinstance(symbol, Terminal):
                first.add(symbol)
                break
            elif isinstance(symbol, NonTerminal):
                if symbol in visited:
                    continue
                visited.add(symbol)
                for rule in symbol.rules:
                    for x in self.FIRST(rule.rhs, visited):
                        first.add(x)
                if not any(self.EPS(rule.rhs) for rule in symbol.rules):
                    break
        
        return first

    def FOLLOW(self, symbol: NonTerminal, visited: Optional[Set[NonTerminal]] = None) -> Set[Terminal]:
        """
        Returns the FOLLOW set of symbol.

        The FOLLOW set contains all terminals which occur right after the given non-terminal symbol
        when derivating from the start symbol S.
        """
        assert isinstance(symbol, NonTerminal),\
            "{} is no NonTerminal".format(symbol)

        follow = set()

        if not visited:
            visited = set()

        for rule in self.grammar.rules:
            for index, value in [(i, v) for i, v in enumerate(rule.rhs) if v == symbol]:
                rest = rule.rhs[(index + 1):]
                for x in self.FIRST(rest):
                    follow.add(x)
                if self.EPS(rest) and rule.lhs not in visited:
                    visited.add(rule.lhs)
                    for x in self.FOLLOW(rule.lhs, visited):
                        follow.add(x)

        return follow

    def PREDICT(self, rule: Rule) -> Set[Terminal]:
        """
        Returns the PREDICT set of a given rule (A -> a) where
        A is a non-terminal and a is an arbitrary word of that grammar.

        The PREDICT set contains at least the FIRST set of the word a.
        If a, however, can become the empty word via derivation then
        the PREDICT set also contains the FOLLOW set of the non-terminal A.
        """
        assert isinstance(rule, Rule), \
            "{} is no rule".format(rule)

        predict = set()

        for x in self.FIRST(rule.rhs):
            predict.add(x)
        if self.EPS(rule.rhs):
            for x in self.FOLLOW(rule.lhs):
                predict.add(x)
        
        return predict
