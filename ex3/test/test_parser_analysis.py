# Unit testing framework
import unittest

# Entities to test
from parserll1.analysis import LL1Analysis
from parserll1.grammar import Terminal


class TestLL1Analysis(unittest.TestCase):
    """A class testing the full implementation of the analyzer class for LL1 grammars."""

    def setUp(self):
        """Defines the grammar and analyzer to test with."""
        # Define grammar to be tested.
        # We use the L.ll1 grammar for testing purposes.
        from parserll1.generator import load_grammar

        grammar_name = "L"
        self.test_grammar = load_grammar(grammar_name)
        self.test_analysis = LL1Analysis(self.test_grammar)

    def test_eps(self):
        """Tests the EPS functionality of the defined analyzer."""
        """
        # Order the rules by the amount of non-terminals on the right-hand side in ascending order.
        # Therefore, if a method does not work as expected, the students start to work on rules having potentially less derivations because of less non-terminals.
        # This may help increasing the debugging effectiveness.

        # Count the amount of non-terminals on the rhs.
        sort_func = lambda rule: len([symbol for symbol in rule.rhs if isinstance(symbol, NonTerminal)])
        sorted_rules = sorted(self.test_grammar.rules, key=sort_func)
        ground_truth = {repr(rule): self.test_analysis.EPS(rule.rhs) for rule in sorted_rules}
        print(ground_truth)
        self.assertTrue(False)
        """
        # What should be calculated.
        expected_results = {
            "NT(type) -> [T(INT)]": False,
            "NT(identifier) -> [T(IDENT)]": False,
            "NT(literal) -> [T(LITERAL)]": False,
            "NT(decl_list) -> [E]": True,
            "NT(param_list) -> [E]": True,
            "NT(param_list_tail) -> [E]": True,
            "NT(stmt_list) -> [E]": True,
            "NT(if_tail) -> [E]": True,
            "NT(expr_tail) -> [E]": True,
            "NT(term_tail) -> [E]": True,
            "NT(factor_tail) -> [E]": True,
            "NT(arg_list) -> [E]": True,
            "NT(arg_list_tail) -> [E]": True,
            "NT(type) -> [T(ET), NT(type)]": False,
            "NT(program) -> [NT(decl_list), T(EOF)]": False,
            "NT(block) -> [T(LBRACE), NT(stmt_list), T(RBRACE)]": False,
            "NT(stmt) -> [NT(var_decl)]": False,
            "NT(stmt) -> [NT(expr), T(SEMICOLON)]": False,
            "NT(stmt) -> [T(RETURN), NT(expr), T(SEMICOLON)]": False,
            "NT(if_tail) -> [T(ELSE), NT(block)]": False,
            "NT(expr_tail) -> [T(ASSIGN), NT(expr)]": False,
            "NT(expr_tail) -> [NT(bool_expr_tail)]": False,
            "NT(factor) -> [NT(literal)]": False,
            "NT(factor) -> [T(NOT), NT(factor)]": False,
            "NT(factor) -> [T(SUB), NT(factor)]": False,
            "NT(factor) -> [T(MUL), NT(factor)]": False,
            "NT(factor) -> [T(ET), NT(factor)]": False,
            "NT(factor) -> [T(LPAR), NT(expr), T(RPAR)]": False,
            "NT(factor_tail) -> [T(LPAR), NT(arg_list), T(RPAR)]": False,
            "NT(bool_expr_tail) -> [T(LE), NT(expr)]": False,
            "NT(bool_expr_tail) -> [T(GE), NT(expr)]": False,
            "NT(bool_expr_tail) -> [T(EQ), NT(expr)]": False,
            "NT(decl_list) -> [NT(func_decl), NT(decl_list)]": False,
            "NT(param_list) -> [NT(param), NT(param_list_tail)]": False,
            "NT(param_list_tail) -> [T(COMMA), NT(param), NT(param_list_tail)]": False,
            "NT(param) -> [NT(identifier), T(COLON), NT(type)]": False,
            "NT(stmt_list) -> [NT(stmt), NT(stmt_list)]": False,
            "NT(stmt) -> [T(WHILE), T(LPAR), NT(expr), T(RPAR), NT(block)]": False,
            "NT(var_decl) -> [T(VAR), NT(identifier), T(COLON), NT(type), T(SEMICOLON)]": False,
            "NT(expr) -> [NT(term), NT(expr_tail)]": False,
            "NT(expr_tail) -> [T(ADD), NT(term), NT(expr_tail)]": False,
            "NT(expr_tail) -> [T(SUB), NT(term), NT(expr_tail)]": False,
            "NT(term) -> [NT(factor), NT(term_tail)]": False,
            "NT(term_tail) -> [T(MUL), NT(factor), NT(term_tail)]": False,
            "NT(term_tail) -> [T(DIV), NT(factor), NT(term_tail)]": False,
            "NT(factor) -> [NT(identifier), NT(factor_tail)]": False,
            "NT(arg_list) -> [NT(expr), NT(arg_list_tail)]": False,
            "NT(arg_list_tail) -> [T(COMMA), NT(expr), NT(arg_list_tail)]": False,
            "NT(stmt) -> [T(IF), T(LPAR), NT(expr), T(RPAR), NT(block), NT(if_tail)]": False,
            "NT(func_decl) -> [T(FUNC), NT(identifier), T(LPAR), NT(param_list), T(RPAR), T(COLON), NT(type), NT(block)]": False,
        }
        errors = {}
        # Check all EPS results.
        for rule in self.test_grammar.rules:
            eps_result = self.test_analysis.EPS(rule.rhs)
            expected_result = expected_results[repr(rule)]
            # Type equality.
            if not (isinstance(eps_result, bool)):
                errors[rule] = {
                    "expected": "type of {}".format(repr(bool)),
                    "given": "type of {}".format(repr(type(eps_result))),
                }
                continue
            # Value equality.
            if eps_result != expected_result:
                errors[rule] = {"expected": "<{}>".format(expected_result), "given": "<{}>".format(eps_result)}
        # Collect all errors.
        error_messages = [
            "[EPS ERROR] rule {} expected to be {} but the result was {}".format(
                repr(rule), rule_result["expected"], rule_result["given"]
            )
            for rule, rule_result in errors.items()
        ]
        # Concatenate all errors.
        full_message = "\n".join(error_messages)
        # There should be no errors at the end.
        self.assertEqual(len(errors), 0, msg=full_message)

    def test_first(self):
        """Tests the FIRST functionality of the defined analyzer."""
        """
        # Order the rules by the amount of non-terminals on the right-hand side in ascending order.
        # Therefore, if a method does not work as expected, the students start to work on rules having potentially less derivations because of less non-terminals.
        # This may help increasing the debugging effectiveness.

        # Count the amount of non-terminals on the rhs.
        sort_func = lambda rule: len([symbol for symbol in rule.rhs if isinstance(symbol, NonTerminal)])
        sorted_rules = sorted(self.test_grammar.rules, key=sort_func)
        ground_truth = {
            repr(rule): "set(({}))".format(
                ''.join(
                    [
                        "Terminal('{}','{}',{},{}),".format(
                            terminal.name,
                            terminal.regex,
                            terminal.skip,
                            terminal.eof,
                        )
                        for terminal in self.test_analysis.FIRST(rule.rhs)
                    ]
                )
            )
            for rule in sorted_rules
        }
        print(ground_truth)
        self.assertTrue(False)
        """
        # What should be calculated.
        expected_results = {
            "NT(type) -> [T(INT)]": set((Terminal("INT", "int", False, False),)),
            "NT(identifier) -> [T(IDENT)]": set((Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)),
            "NT(literal) -> [T(LITERAL)]": set((Terminal("LITERAL", "[0-9]+", False, False),)),
            "NT(decl_list) -> [E]": set(()),
            "NT(param_list) -> [E]": set(()),
            "NT(param_list_tail) -> [E]": set(()),
            "NT(stmt_list) -> [E]": set(()),
            "NT(if_tail) -> [E]": set(()),
            "NT(expr_tail) -> [E]": set(()),
            "NT(term_tail) -> [E]": set(()),
            "NT(factor_tail) -> [E]": set(()),
            "NT(arg_list) -> [E]": set(()),
            "NT(arg_list_tail) -> [E]": set(()),
            "NT(type) -> [T(ET), NT(type)]": set((Terminal("ET", "&", False, False),)),
            "NT(program) -> [NT(decl_list), T(EOF)]": set(
                (
                    Terminal("EOF", "$", False, False),
                    Terminal("FUNC", "func", False, False),
                )
            ),
            "NT(block) -> [T(LBRACE), NT(stmt_list), T(RBRACE)]": set((Terminal("LBRACE", "{", False, False),)),
            "NT(stmt) -> [NT(var_decl)]": set((Terminal("VAR", "var", False, False),)),
            "NT(stmt) -> [NT(expr), T(SEMICOLON)]": set(
                (
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("SUB", "-", False, False),
                )
            ),
            "NT(stmt) -> [T(RETURN), NT(expr), T(SEMICOLON)]": set((Terminal("RETURN", "return", False, False),)),
            "NT(if_tail) -> [T(ELSE), NT(block)]": set((Terminal("ELSE", "else", False, False),)),
            "NT(expr_tail) -> [T(ASSIGN), NT(expr)]": set((Terminal("ASSIGN", ":=", False, False),)),
            "NT(expr_tail) -> [NT(bool_expr_tail)]": set(
                (
                    Terminal("EQ", "==", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("LE", "<=", False, False),
                )
            ),
            "NT(factor) -> [NT(literal)]": set((Terminal("LITERAL", "[0-9]+", False, False),)),
            "NT(factor) -> [T(NOT), NT(factor)]": set((Terminal("NOT", "!", False, False),)),
            "NT(factor) -> [T(SUB), NT(factor)]": set((Terminal("SUB", "-", False, False),)),
            "NT(factor) -> [T(MUL), NT(factor)]": set((Terminal("MUL", "[*]", False, False),)),
            "NT(factor) -> [T(ET), NT(factor)]": set((Terminal("ET", "&", False, False),)),
            "NT(factor) -> [T(LPAR), NT(expr), T(RPAR)]": set((Terminal("LPAR", "\\(", False, False),)),
            "NT(factor_tail) -> [T(LPAR), NT(arg_list), T(RPAR)]": set((Terminal("LPAR", "\\(", False, False),)),
            "NT(bool_expr_tail) -> [T(LE), NT(expr)]": set((Terminal("LE", "<=", False, False),)),
            "NT(bool_expr_tail) -> [T(GE), NT(expr)]": set((Terminal("GE", ">=", False, False),)),
            "NT(bool_expr_tail) -> [T(EQ), NT(expr)]": set((Terminal("EQ", "==", False, False),)),
            "NT(decl_list) -> [NT(func_decl), NT(decl_list)]": set((Terminal("FUNC", "func", False, False),)),
            "NT(param_list) -> [NT(param), NT(param_list_tail)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(param_list_tail) -> [T(COMMA), NT(param), NT(param_list_tail)]": set(
                (Terminal("COMMA", ",", False, False),)
            ),
            "NT(param) -> [NT(identifier), T(COLON), NT(type)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(stmt_list) -> [NT(stmt), NT(stmt_list)]": set(
                (
                    Terminal("VAR", "var", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("IF", "if", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("SUB", "-", False, False),
                )
            ),
            "NT(stmt) -> [T(WHILE), T(LPAR), NT(expr), T(RPAR), NT(block)]": set(
                (Terminal("WHILE", "while", False, False),)
            ),
            "NT(var_decl) -> [T(VAR), NT(identifier), T(COLON), NT(type), T(SEMICOLON)]": set(
                (Terminal("VAR", "var", False, False),)
            ),
            "NT(expr) -> [NT(term), NT(expr_tail)]": set(
                (
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("SUB", "-", False, False),
                )
            ),
            "NT(expr_tail) -> [T(ADD), NT(term), NT(expr_tail)]": set((Terminal("ADD", "[+]", False, False),)),
            "NT(expr_tail) -> [T(SUB), NT(term), NT(expr_tail)]": set((Terminal("SUB", "-", False, False),)),
            "NT(term) -> [NT(factor), NT(term_tail)]": set(
                (
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("SUB", "-", False, False),
                )
            ),
            "NT(term_tail) -> [T(MUL), NT(factor), NT(term_tail)]": set((Terminal("MUL", "[*]", False, False),)),
            "NT(term_tail) -> [T(DIV), NT(factor), NT(term_tail)]": set((Terminal("DIV", "/", False, False),)),
            "NT(factor) -> [NT(identifier), NT(factor_tail)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(arg_list) -> [NT(expr), NT(arg_list_tail)]": set(
                (
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("SUB", "-", False, False),
                )
            ),
            "NT(arg_list_tail) -> [T(COMMA), NT(expr), NT(arg_list_tail)]": set(
                (Terminal("COMMA", ",", False, False),)
            ),
            "NT(stmt) -> [T(IF), T(LPAR), NT(expr), T(RPAR), NT(block), NT(if_tail)]": set(
                (Terminal("IF", "if", False, False),)
            ),
            "NT(func_decl) -> [T(FUNC), NT(identifier), T(LPAR), NT(param_list), T(RPAR), T(COLON), NT(type), NT(block)]": set(
                (Terminal("FUNC", "func", False, False),)
            ),
        }
        errors = {}
        # Check all FIRST results.
        for rule in self.test_grammar.rules:
            first_result = self.test_analysis.FIRST(rule.rhs)
            expected_result = expected_results[repr(rule)]
            # Type equality
            if not (isinstance(first_result, set)):
                errors[rule] = {
                    "expected": "type of {}".format(repr(set)),
                    "given": "type of {}".format(repr(type(first_result))),
                }
                continue
            # Value equality. Compare for string representation of sets.
            first_result_as_string_set = set([repr(terminal) for terminal in first_result])
            expected_result_as_string_set = set([repr(terminal) for terminal in expected_result])

            if first_result_as_string_set != expected_result_as_string_set:
                errors[rule] = {"expected": "<{}>".format(expected_result), "given": "<{}>".format(first_result)}
        # Collect all errors.
        error_messages = [
            "[FIRST ERROR] rule {} expected to be {} but the result was {}".format(
                repr(rule), rule_result["expected"], rule_result["given"]
            )
            for rule, rule_result in errors.items()
        ]
        # Concatenate all errors.
        full_message = "\n".join(error_messages)
        # There should be no errors at the end.
        self.assertEqual(len(errors), 0, msg=full_message)

    def test_follow(self):
        """Tests the FOLLOW functionality of the defined analyzer."""
        """
        # Order the rules by the amount of non-terminals on the right-hand side in ascending order.
        # Therefore, if a method does not work as expected, the students start to work on rules having potentially less derivations because of less non-terminals.
        # This may help increasing the debugging effectiveness.

        # Count the amount of non-terminals on the rhs.
        sort_func = lambda rule: len([symbol for symbol in rule.rhs if isinstance(symbol, NonTerminal)])
        sorted_rules = sorted(self.test_grammar.rules, key=sort_func)
        ground_truth = {
            repr(rule): "set(({}))".format(
                ''.join(
                    [
                        "Terminal('{}','{}',{},{}),".format(
                            terminal.name,
                            terminal.regex,
                            terminal.skip,
                            terminal.eof,
                        )
                        for terminal in self.test_analysis.FOLLOW(rule.lhs)
                    ]
                )
            )
            for rule in sorted_rules
        }
        print(ground_truth)
        self.assertTrue(False)
        """
        # What should be calculated.
        expected_results = {
            "NT(type) -> [T(INT)]": set(
                (
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("LBRACE", "{", False, False),
                )
            ),
            "NT(identifier) -> [T(IDENT)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("COLON", ":", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(literal) -> [T(LITERAL)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(decl_list) -> [E]": set((Terminal("EOF", "$", False, False),)),
            "NT(param_list) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(param_list_tail) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(stmt_list) -> [E]": set((Terminal("RBRACE", "}", False, False),)),
            "NT(if_tail) -> [E]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(expr_tail) -> [E]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(term_tail) -> [E]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(factor_tail) -> [E]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(arg_list) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(arg_list_tail) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(type) -> [T(ET), NT(type)]": set(
                (
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("LBRACE", "{", False, False),
                )
            ),
            "NT(program) -> [NT(decl_list), T(EOF)]": set(()),
            "NT(block) -> [T(LBRACE), NT(stmt_list), T(RBRACE)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("FUNC", "func", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("ELSE", "else", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("EOF", "$", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(stmt) -> [NT(var_decl)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(stmt) -> [NT(expr), T(SEMICOLON)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(stmt) -> [T(RETURN), NT(expr), T(SEMICOLON)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(if_tail) -> [T(ELSE), NT(block)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(expr_tail) -> [T(ASSIGN), NT(expr)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(expr_tail) -> [NT(bool_expr_tail)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [NT(literal)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [T(NOT), NT(factor)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [T(SUB), NT(factor)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [T(MUL), NT(factor)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [T(ET), NT(factor)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor) -> [T(LPAR), NT(expr), T(RPAR)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(factor_tail) -> [T(LPAR), NT(arg_list), T(RPAR)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(bool_expr_tail) -> [T(LE), NT(expr)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(bool_expr_tail) -> [T(GE), NT(expr)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(bool_expr_tail) -> [T(EQ), NT(expr)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(decl_list) -> [NT(func_decl), NT(decl_list)]": set((Terminal("EOF", "$", False, False),)),
            "NT(param_list) -> [NT(param), NT(param_list_tail)]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(param_list_tail) -> [T(COMMA), NT(param), NT(param_list_tail)]": set(
                (Terminal("RPAR", "\\)", False, False),)
            ),
            "NT(param) -> [NT(identifier), T(COLON), NT(type)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(stmt_list) -> [NT(stmt), NT(stmt_list)]": set((Terminal("RBRACE", "}", False, False),)),
            "NT(stmt) -> [T(WHILE), T(LPAR), NT(expr), T(RPAR), NT(block)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(var_decl) -> [T(VAR), NT(identifier), T(COLON), NT(type), T(SEMICOLON)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(expr) -> [NT(term), NT(expr_tail)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(expr_tail) -> [T(ADD), NT(term), NT(expr_tail)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(expr_tail) -> [T(SUB), NT(term), NT(expr_tail)]": set(
                (
                    Terminal("COMMA", ",", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(term) -> [NT(factor), NT(term_tail)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(term_tail) -> [T(MUL), NT(factor), NT(term_tail)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(term_tail) -> [T(DIV), NT(factor), NT(term_tail)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(factor) -> [NT(identifier), NT(factor_tail)]": set(
                (
                    Terminal("LE", "<=", False, False),
                    Terminal("ADD", "[+]", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("GE", ">=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(arg_list) -> [NT(expr), NT(arg_list_tail)]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(arg_list_tail) -> [T(COMMA), NT(expr), NT(arg_list_tail)]": set(
                (Terminal("RPAR", "\\)", False, False),)
            ),
            "NT(stmt) -> [T(IF), T(LPAR), NT(expr), T(RPAR), NT(block), NT(if_tail)]": set(
                (
                    Terminal("IF", "if", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(func_decl) -> [T(FUNC), NT(identifier), T(LPAR), NT(param_list), T(RPAR), T(COLON), NT(type), NT(block)]": set(
                (
                    Terminal("FUNC", "func", False, False),
                    Terminal("EOF", "$", False, False),
                )
            ),
        }
        errors = {}
        # Check all FOLLOW results.
        for rule in self.test_grammar.rules:
            first_result = self.test_analysis.FOLLOW(rule.lhs)
            expected_result = expected_results[repr(rule)]
            # Type equality
            if not (isinstance(first_result, set)):
                errors[rule] = {
                    "expected": "type of {}".format(repr(set)),
                    "given": "type of {}".format(repr(type(first_result))),
                }
                continue
            # Value equality. Compare for string representation of sets.
            first_result_as_string_set = set([repr(terminal) for terminal in first_result])
            expected_result_as_string_set = set([repr(terminal) for terminal in expected_result])

            if first_result_as_string_set != expected_result_as_string_set:
                errors[rule] = {"expected": "<{}>".format(expected_result), "given": "<{}>".format(first_result)}
        # Collect all errors.
        error_messages = [
            "[FOLLOW ERROR] rule {} expected to be {} but the result was {}".format(
                repr(rule), rule_result["expected"], rule_result["given"]
            )
            for rule, rule_result in errors.items()
        ]
        # Concatenate all errors.
        full_message = "\n".join(error_messages)
        # There should be no errors at the end.
        self.assertEqual(len(errors), 0, msg=full_message)

    def test_predict(self):
        """Tests the PREDICT functionality of the defined analyzer."""
        """
        # Order the rules by the amount of non-terminals on the right-hand side in ascending order.
        # Therefore, if a method does not work as expected, the students start to work on rules having potentially less derivations because of less non-terminals.
        # This may help increasing the debugging effectiveness.

        # Count the amount of non-terminals on the rhs.
        sort_func = lambda rule: len([symbol for symbol in rule.rhs if isinstance(symbol, NonTerminal)])
        sorted_rules = sorted(self.test_grammar.rules, key=sort_func)
        ground_truth = {
            repr(rule): "set(({}))".format(
                ''.join(
                    [
                        "Terminal('{}','{}',{},{}),".format(
                            terminal.name,
                            terminal.regex,
                            terminal.skip,
                            terminal.eof,
                        )
                        for terminal in self.test_analysis.PREDICT(rule)
                    ]
                )
            )
            for rule in sorted_rules
        }
        print(ground_truth)
        self.assertTrue(False)
        """
        # What should be calculated.
        expected_results = {
            "NT(type) -> [T(INT)]": set((Terminal("INT", "int", False, False),)),
            "NT(identifier) -> [T(IDENT)]": set((Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)),
            "NT(literal) -> [T(LITERAL)]": set((Terminal("LITERAL", "[0-9]+", False, False),)),
            "NT(decl_list) -> [E]": set((Terminal("EOF", "$", False, False),)),
            "NT(param_list) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(param_list_tail) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(stmt_list) -> [E]": set((Terminal("RBRACE", "}", False, False),)),
            "NT(if_tail) -> [E]": set(
                (
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("RBRACE", "}", False, False),
                    Terminal("IF", "if", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(expr_tail) -> [E]": set(
                (
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                )
            ),
            "NT(term_tail) -> [E]": set(
                (
                    Terminal("ADD", "[+]", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("LE", "<=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(factor_tail) -> [E]": set(
                (
                    Terminal("ADD", "[+]", False, False),
                    Terminal("ASSIGN", ":=", False, False),
                    Terminal("SEMICOLON", ";", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("COMMA", ",", False, False),
                    Terminal("RPAR", "\\)", False, False),
                    Terminal("DIV", "/", False, False),
                    Terminal("LE", "<=", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("EQ", "==", False, False),
                    Terminal("GE", ">=", False, False),
                )
            ),
            "NT(arg_list) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(arg_list_tail) -> [E]": set((Terminal("RPAR", "\\)", False, False),)),
            "NT(type) -> [T(ET), NT(type)]": set((Terminal("ET", "&", False, False),)),
            "NT(program) -> [NT(decl_list), T(EOF)]": set(
                (
                    Terminal("EOF", "$", False, False),
                    Terminal("FUNC", "func", False, False),
                )
            ),
            "NT(block) -> [T(LBRACE), NT(stmt_list), T(RBRACE)]": set((Terminal("LBRACE", "{", False, False),)),
            "NT(stmt) -> [NT(var_decl)]": set((Terminal("VAR", "var", False, False),)),
            "NT(stmt) -> [NT(expr), T(SEMICOLON)]": set(
                (
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                )
            ),
            "NT(stmt) -> [T(RETURN), NT(expr), T(SEMICOLON)]": set((Terminal("RETURN", "return", False, False),)),
            "NT(if_tail) -> [T(ELSE), NT(block)]": set((Terminal("ELSE", "else", False, False),)),
            "NT(expr_tail) -> [T(ASSIGN), NT(expr)]": set((Terminal("ASSIGN", ":=", False, False),)),
            "NT(expr_tail) -> [NT(bool_expr_tail)]": set(
                (
                    Terminal("GE", ">=", False, False),
                    Terminal("LE", "<=", False, False),
                    Terminal("EQ", "==", False, False),
                )
            ),
            "NT(factor) -> [NT(literal)]": set((Terminal("LITERAL", "[0-9]+", False, False),)),
            "NT(factor) -> [T(NOT), NT(factor)]": set((Terminal("NOT", "!", False, False),)),
            "NT(factor) -> [T(SUB), NT(factor)]": set((Terminal("SUB", "-", False, False),)),
            "NT(factor) -> [T(MUL), NT(factor)]": set((Terminal("MUL", "[*]", False, False),)),
            "NT(factor) -> [T(ET), NT(factor)]": set((Terminal("ET", "&", False, False),)),
            "NT(factor) -> [T(LPAR), NT(expr), T(RPAR)]": set((Terminal("LPAR", "\\(", False, False),)),
            "NT(factor_tail) -> [T(LPAR), NT(arg_list), T(RPAR)]": set((Terminal("LPAR", "\\(", False, False),)),
            "NT(bool_expr_tail) -> [T(LE), NT(expr)]": set((Terminal("LE", "<=", False, False),)),
            "NT(bool_expr_tail) -> [T(GE), NT(expr)]": set((Terminal("GE", ">=", False, False),)),
            "NT(bool_expr_tail) -> [T(EQ), NT(expr)]": set((Terminal("EQ", "==", False, False),)),
            "NT(decl_list) -> [NT(func_decl), NT(decl_list)]": set((Terminal("FUNC", "func", False, False),)),
            "NT(param_list) -> [NT(param), NT(param_list_tail)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(param_list_tail) -> [T(COMMA), NT(param), NT(param_list_tail)]": set(
                (Terminal("COMMA", ",", False, False),)
            ),
            "NT(param) -> [NT(identifier), T(COLON), NT(type)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(stmt_list) -> [NT(stmt), NT(stmt_list)]": set(
                (
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("VAR", "var", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                    Terminal("RETURN", "return", False, False),
                    Terminal("WHILE", "while", False, False),
                    Terminal("IF", "if", False, False),
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                )
            ),
            "NT(stmt) -> [T(WHILE), T(LPAR), NT(expr), T(RPAR), NT(block)]": set(
                (Terminal("WHILE", "while", False, False),)
            ),
            "NT(var_decl) -> [T(VAR), NT(identifier), T(COLON), NT(type), T(SEMICOLON)]": set(
                (Terminal("VAR", "var", False, False),)
            ),
            "NT(expr) -> [NT(term), NT(expr_tail)]": set(
                (
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                )
            ),
            "NT(expr_tail) -> [T(ADD), NT(term), NT(expr_tail)]": set((Terminal("ADD", "[+]", False, False),)),
            "NT(expr_tail) -> [T(SUB), NT(term), NT(expr_tail)]": set((Terminal("SUB", "-", False, False),)),
            "NT(term) -> [NT(factor), NT(term_tail)]": set(
                (
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                )
            ),
            "NT(term_tail) -> [T(MUL), NT(factor), NT(term_tail)]": set((Terminal("MUL", "[*]", False, False),)),
            "NT(term_tail) -> [T(DIV), NT(factor), NT(term_tail)]": set((Terminal("DIV", "/", False, False),)),
            "NT(factor) -> [NT(identifier), NT(factor_tail)]": set(
                (Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),)
            ),
            "NT(arg_list) -> [NT(expr), NT(arg_list_tail)]": set(
                (
                    Terminal("SUB", "-", False, False),
                    Terminal("NOT", "!", False, False),
                    Terminal("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False, False),
                    Terminal("ET", "&", False, False),
                    Terminal("LPAR", "\\(", False, False),
                    Terminal("MUL", "[*]", False, False),
                    Terminal("LITERAL", "[0-9]+", False, False),
                )
            ),
            "NT(arg_list_tail) -> [T(COMMA), NT(expr), NT(arg_list_tail)]": set(
                (Terminal("COMMA", ",", False, False),)
            ),
            "NT(stmt) -> [T(IF), T(LPAR), NT(expr), T(RPAR), NT(block), NT(if_tail)]": set(
                (Terminal("IF", "if", False, False),)
            ),
            "NT(func_decl) -> [T(FUNC), NT(identifier), T(LPAR), NT(param_list), T(RPAR), T(COLON), NT(type), NT(block)]": set(
                (Terminal("FUNC", "func", False, False),)
            ),
        }
        errors = {}
        # Check all PREDICT results.
        for rule in self.test_grammar.rules:
            first_result = self.test_analysis.PREDICT(rule)
            expected_result = expected_results[repr(rule)]
            # Type equality
            if not (isinstance(first_result, set)):
                errors[rule] = {
                    "expected": "type of {}".format(repr(set)),
                    "given": "type of {}".format(repr(type(first_result))),
                }
                continue
            # Value equality. Compare for string representation of sets.
            first_result_as_string_set = set([repr(terminal) for terminal in first_result])
            expected_result_as_string_set = set([repr(terminal) for terminal in expected_result])

            if first_result_as_string_set != expected_result_as_string_set:
                errors[rule] = {"expected": "<{}>".format(expected_result), "given": "<{}>".format(first_result)}
        # Collect all errors.
        error_messages = [
            "[PREDICT ERROR] rule {} expected to be {} but the result was {}".format(
                repr(rule), rule_result["expected"], rule_result["given"]
            )
            for rule, rule_result in errors.items()
        ]
        # Concatenate all errors.
        full_message = "\n".join(error_messages)
        # There should be no errors at the end.
        self.assertEqual(len(errors), 0, msg=full_message)


# Start unit testing when module is directly loaded.
if __name__ == "__main__":
    unittest.main()
