################################################################
from parserll1.scanner import BaseScanner


class Scanner(BaseScanner):
    scanner_table = [
        ("EPSILON", "EPSILON", False),
        ("Ident", "[a-zA-Z_][a-zA-Z0-9_]*", False),
        ("String", '"([^"]|\\")*?"', False),
        ("Action", "{[^}]*}", False),
        ("OR", "[|]", False),
        ("EOF", "$", False),
        ("OPT", "%[A-Z]*", False),
        ("GETS", "->", False),
        ("EOL", ";", False),
        ("WS", "[\n\t ]+", True),
        ("COMMENT", "#.*\n", True),
    ]


################################################################
import parserll1.grammar as G


def S(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(S) -> [NT(rule_list), T(EOF)]): {T(Ident), T(OPT), T(EOF)}
    if token_stream.peek() in ["Ident", "OPT", "EOF"]:
        var_0 = rule_list(token_stream, parse_tree)
        var_1 = token_stream.read(expected="EOF")
        if not parse_tree:
            return ["grammar"] + var_0
        return ["S", var_0, var_1]
    token_stream.raise_error()


def opt(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(opt) -> [T(OPT), T(Ident), NT(opt_tail)]): {T(OPT)}
    if token_stream.peek() in ["OPT"]:
        var_0 = token_stream.read(expected="OPT")
        var_1 = token_stream.read(expected="Ident")
        var_2 = opt_tail(token_stream, parse_tree)
        return ["opt", var_0, var_1, var_2]
    token_stream.raise_error()


def opt_tail(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(opt_tail) -> [E]): {T(Ident), T(OPT), T(EOF)}
    if token_stream.peek() in ["Ident", "OPT", "EOF"]:
        # Skip Epsilon
        if not parse_tree:
            return None
        return ["opt_tail"]
    #  PREDICT(NT(opt_tail) -> [T(String)]): {T(String)}
    if token_stream.peek() in ["String"]:
        var_0 = token_stream.read(expected="String")
        if not parse_tree:
            return var_0.load
        return ["opt_tail", var_0]
    token_stream.raise_error()


def rule_list(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(rule_list) -> [NT(opt), NT(rule_list)]): {T(OPT)}
    if token_stream.peek() in ["OPT"]:
        var_0 = opt(token_stream, parse_tree)
        var_1 = rule_list(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["rule_list", var_0, var_1]
    #  PREDICT(NT(rule_list) -> [NT(rule), NT(rule_list)]): {T(Ident)}
    if token_stream.peek() in ["Ident"]:
        var_0 = rule(token_stream, parse_tree)
        var_1 = rule_list(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["rule_list", var_0, var_1]
    #  PREDICT(NT(rule_list) -> [E]): {T(EOF)}
    if token_stream.peek() in ["EOF"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["rule_list"]
    token_stream.raise_error()


def rule(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(rule) -> [T(Ident), T(GETS), NT(production_list), T(EOL)]): {T(Ident)}
    if token_stream.peek() in ["Ident"]:
        var_0 = token_stream.read(expected="Ident")
        var_1 = token_stream.read(expected="GETS")
        var_2 = production_list(token_stream, parse_tree)
        var_3 = token_stream.read(expected="EOL")
        if not parse_tree:
            return ["rule", var_0, var_2]
        return ["rule", var_0, var_1, var_2, var_3]
    token_stream.raise_error()


def production_list(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(production_list) -> [NT(production), NT(production_list_tail)]): {T(EPSILON), T(Ident)}
    if token_stream.peek() in ["EPSILON", "Ident"]:
        var_0 = production(token_stream, parse_tree)
        var_1 = production_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return ["production_list", var_0] + var_1
        return ["production_list", var_0, var_1]
    token_stream.raise_error()


def production_list_tail(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(production_list_tail) -> [T(OR), NT(production), NT(production_list_tail)]): {T(OR)}
    if token_stream.peek() in ["OR"]:
        var_0 = token_stream.read(expected="OR")
        var_1 = production(token_stream, parse_tree)
        var_2 = production_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_1] + var_2
        return ["production_list_tail", var_0, var_1, var_2]
    #  PREDICT(NT(production_list_tail) -> [E]): {T(EOL)}
    if token_stream.peek() in ["EOL"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["production_list_tail"]
    token_stream.raise_error()


def production(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(production) -> [NT(word), NT(production_tail)]): {T(EPSILON), T(Ident)}
    if token_stream.peek() in ["EPSILON", "Ident"]:
        var_0 = word(token_stream, parse_tree)
        var_1 = production_tail(token_stream, parse_tree)
        if not parse_tree:
            return ["production", var_0, var_1]
        return ["production", var_0, var_1]
    token_stream.raise_error()


def production_tail(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(production_tail) -> [T(Action)]): {T(Action)}
    if token_stream.peek() in ["Action"]:
        var_0 = token_stream.read(expected="Action")
        if not parse_tree:
            return var_0.load
        return ["production_tail", var_0]
    #  PREDICT(NT(production_tail) -> [E]): {T(OR), T(EOL)}
    if token_stream.peek() in ["OR", "EOL"]:
        # Skip Epsilon
        if not parse_tree:
            return None
        return ["production_tail"]
    token_stream.raise_error()


def word(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(word) -> [NT(symbol), NT(word_tail)]): {T(EPSILON), T(Ident)}
    if token_stream.peek() in ["EPSILON", "Ident"]:
        var_0 = symbol(token_stream, parse_tree)
        var_1 = word_tail(token_stream, parse_tree)
        if not parse_tree:
            return ["word", var_0] + var_1
        return ["word", var_0, var_1]
    token_stream.raise_error()


def word_tail(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(word_tail) -> [NT(symbol), NT(word_tail)]): {T(EPSILON), T(Ident)}
    if token_stream.peek() in ["EPSILON", "Ident"]:
        var_0 = symbol(token_stream, parse_tree)
        var_1 = word_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["word_tail", var_0, var_1]
    #  PREDICT(NT(word_tail) -> [E]): {T(OR), T(Action), T(EOL)}
    if token_stream.peek() in ["OR", "Action", "EOL"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["word_tail"]
    token_stream.raise_error()


def symbol(token_stream: BaseScanner, parse_tree=False):
    #  PREDICT(NT(symbol) -> [T(EPSILON)]): {T(EPSILON)}
    if token_stream.peek() in ["EPSILON"]:
        var_0 = token_stream.read(expected="EPSILON")
        if not parse_tree:
            return var_0.load
        return ["symbol", var_0]
    #  PREDICT(NT(symbol) -> [T(Ident)]): {T(Ident)}
    if token_stream.peek() in ["Ident"]:
        var_0 = token_stream.read(expected="Ident")
        if not parse_tree:
            return var_0.load
        return ["symbol", var_0]
    token_stream.raise_error()


def parse(text, *args, **kwargs):
    scanner = Scanner(text)
    return S(scanner, *args, **kwargs)


# Utility methods for pretty printing the generated grammar sequence.
def __get_blue_text__(text):
    return "\033[94m" + text + "\033[0m"


def __get_green_text__(text):
    return "\033[92m" + text + "\033[0m"


def __printi__(text, indent=0):
    print(" " * indent + str(text))


def __print_instruction_plane__(instr_plane, indent=0):
    # Needed if built in type function has been overwritten.
    import builtins

    for index, instr in enumerate(instr_plane):
        # Next transition.
        if (builtins.type(instr)) == list:
            __print_instruction_plane__(instr, indent + 5)
        # Transition name.
        elif (builtins.type(instr)) == str:
            # Align first child for AST presentation purposes.
            if index == 0:
                __printi__(__get_green_text__("[NT] " + instr), indent)
            else:
                __printi__(__get_green_text__("[NT] " + instr), indent)
        # Token name.
        else:
            __printi__(__get_blue_text__("[T]  " + str(instr)), indent + 5)


def pprint(text, *args, **kwargs):
    # Needed if built in type function has been overwritten.
    import builtins

    scanner = Scanner(text)
    scanner_result = S(scanner, *args, **kwargs)

    if builtins.type(scanner_result) == list:
        print("=== Parsed statement start ===")
        __print_instruction_plane__(scanner_result)
        print("=== Parsed statement end ===")
    else:
        print(str(scanner_result))
