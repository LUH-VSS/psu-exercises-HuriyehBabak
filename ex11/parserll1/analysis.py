from parserll1.grammar import Terminal, NonTerminal, Epsilon, isWord, Rule


class AnalysisError(RuntimeError):
    pass


class LL1Analysis:
    def __init__(self, grammar):
        self.grammar = grammar

    def EPS(self, word, visited=None) -> bool:
        """
        Returns true if all non-terminals within word can result
        in the empty word via their derivations.
        """
        # {{BEGIN(L1)}}
        assert isWord(word), "{} is no word".format(word)

        if visited is None:
            visited = set()

        for symbol in word:
            if isinstance(symbol, Epsilon):
                continue  # Just skip epsilons
            elif isinstance(symbol, Terminal):
                return False
            elif isinstance(symbol, NonTerminal):
                # We already were here. This should not happen
                assert symbol not in visited, "There is an endless epsilon recursion"
                visited.add(symbol)

                # If any right-hand side of that non-terminal becomes epsilon, we can become epsilon
                can_diminish = False
                for rule in symbol.rules:
                    if self.EPS(rule.rhs, visited) is True:
                        can_diminish = True
                if not can_diminish:
                    return False
            else:
                raise AnalysisError("Unknown symbol: {}.".format(symbol))
        return True
        # {{END(L1)}}

    def FIRST(self, word, visited=None) -> set:
        """
        Returns the FIRST set of word.

        The FIRST set contains all terminals which occur first at the right side of a derivation
        of a given non-terminal.
        """
        # {{BEGIN(L1)}}
        assert isWord(word), "{} is no word".format(word)

        if visited is None:
            visited = set()

        first_set = set()
        for symbol in word:
            if isinstance(symbol, Epsilon):
                continue  # Just skip epsilons
            elif isinstance(symbol, Terminal):
                first_set.add(symbol)  # Add terminals if they occur on their own.
                break
            elif isinstance(symbol, NonTerminal):
                for rule in symbol.rules:
                    assert rule not in visited, "Endless recursion in grammar rule: {}".format(rule)
                    visited.add(rule)

                    # Merge FIRST sets.
                    first_set |= self.FIRST(rule.rhs, visited)

                # if any rule (symbol -> $rule) can become epsilon, we continue our search
                if any([self.EPS(rule.rhs) for rule in symbol.rules]):
                    continue

                break
        return first_set
        # {{END(L1)}}

    def FOLLOW(self, symbol, visited=None) -> set:
        """
        Returns the FOLLOW set of symbol.

        The FOLLOW set contains all terminals which occur right after the given non-terminal symbol
        when derivating from the start symbol S.
        """
        # {{BEGIN(L1)}}
        assert isinstance(symbol, NonTerminal), "{} is no NonTerminal".format(symbol)

        if visited is None:
            visited = set()

        follow_set = set()

        for rule in self.grammar.rules:
            # Find all occurences of symbol, may be empty
            occurences = [idx for idx, item in enumerate(rule.rhs) if item == symbol]

            for idx in occurences:
                # Pick up all the remaining words right after the symbol.
                # E.g. with symbol A and the word ['a', 'A', 'c', 'B']
                # rest_word is ['c', 'B']
                rest_word = rule.rhs[idx + 1 :]
                follow_set |= self.FIRST(rest_word)
                # If the rest word can be the empty word after (numerous) derivations and
                # we did not operate on the left-hand non-terminal yet then we also add
                # the FOLLOW set of this non-terminal.
                if self.EPS(rest_word) and rule.lhs not in visited:
                    visited.add(rule.lhs)
                    follow_set |= self.FOLLOW(rule.lhs, visited)

        return follow_set
        # {{END(L1)}}

    def PREDICT(self, rule) -> set:
        """
        Returns the PREDICT set of a given rule (A -> a) where
        A is a non-terminal and a is an arbitrary word of that grammar.

        The PREDICT set contains at least the FIRST set of the word a.
        If a, however, can become the empty word via derivation then
        the PREDICT set also contains the FOLLOW set of the non-terminal A.
        """
        # {{BEGIN(L1)}}
        assert isinstance(rule, Rule), "{} is no rule".format(rule)

        predict_set = self.FIRST(rule.rhs)
        if self.EPS(rule.rhs):
            predict_set |= self.FOLLOW(rule.lhs)

        return predict_set
        # {{END(L1)}}
        # {{BEGIN(A1)}}
        # Um Aufgabe 5 bearbeiten zu können, wenn es Probleme bei Aufgabe 4 gibt, wurde die PREDICT-Menge bereits berechnet.
        # Bei erfolgreicher Bearbeitung von Aufgabe 4 kann der folgende Code dementsprechend gelöscht werden.
        cache = {
            "[NT(mathHead), T(Int), T(EOF)]": {
                Terminal("add"),
                Terminal("Int"),
                Terminal("div"),
                Terminal("sub"),
                Terminal("mul"),
            },
            "[T(add), T(Int), NT(mathHead)]": {Terminal("add")},
            "[T(sub), T(Int), NT(mathHead)]": {Terminal("sub")},
            "[T(mul), T(Int), NT(mathHead)]": {Terminal("mul")},
            "[T(div), T(Int), NT(mathHead)]": {Terminal("div")},
            "[E]": {Terminal("Int")},
        }
        return cache.get(repr(rule.rhs))
        # {{END(A1)}}
