import re
import sys
import os
import pathlib
import importlib
import logging
from parserll1.grammar import Terminal, Epsilon, Grammar
from parserll1.analysis import LL1Analysis


# Get an instance of a logger
logger = logging.getLogger("parser")


class ParserGenerator:
    """Creates a parser for a given grammar.

    A parser is able to decide whether a given text is part of the language defined by a specific grammar.
    The text has to follow the syntactic rules of the specified grammar to be part of the language.
    """

    def __init__(self, grammar):
        self.grammar = grammar
        # Uses a lookahead of 1 token for analyzation purposes.
        self.analysis = LL1Analysis(grammar)

    def __gen_pretty_print__(self, writeLn):
        """Creates pretty print methods for the parser.

        :param writeLn: A function used to write the output.
        """
        writeLn()
        writeLn()
        writeLn("# Utility methods for pretty printing the generated grammar sequence.")
        writeLn("def __get_blue_text__(text):")
        writeLn("    return '\\033[94m' + text + '\\033[0m'")
        writeLn()
        writeLn()
        writeLn("def __get_green_text__(text):")
        writeLn("    return '\\033[92m' + text + '\\033[0m'")
        writeLn()
        writeLn()
        writeLn("def __printi__(text, indent=0):")
        writeLn("    print(' ' * indent + str(text))")
        writeLn()
        writeLn()
        writeLn("def __print_instruction_plane__(instr_plane, indent=0):")
        writeLn("    # Needed if built in type function has been overwritten.")
        writeLn("    import builtins")
        writeLn("    for index, instr in enumerate(instr_plane):")
        writeLn("        # Next transition.")
        writeLn("        if(builtins.type(instr)) == list:")
        writeLn("            __print_instruction_plane__(instr, indent + 5)")
        writeLn("        # Transition name.")
        writeLn("        elif (builtins.type(instr)) == str:")
        writeLn("            # Align first child for AST presentation purposes.")
        writeLn("            if(index == 0):")
        writeLn('                __printi__(__get_green_text__("[NT] " + instr), indent)')
        writeLn("            else:")
        writeLn('                __printi__(__get_green_text__("[NT] " + instr), indent)')
        writeLn("        # Token name.")
        writeLn("        else:")
        writeLn('            __printi__(__get_blue_text__("[T]  " + str(instr)), indent + 5)')
        writeLn()
        writeLn()
        writeLn("def pprint(text, *args, **kwargs):")
        writeLn("    # Needed if built in type function has been overwritten.")
        writeLn("    import builtins")
        writeLn()
        writeLn("    scanner = Scanner(text)")
        writeLn("    scanner_result = {}(scanner, *args, **kwargs)".format(self.grammar.start_symbol.name))
        writeLn()
        writeLn("    if builtins.type(scanner_result) == list:")
        writeLn("        print('=== Parsed statement start ===')")
        writeLn("        __print_instruction_plane__(scanner_result)")
        writeLn("        print('=== Parsed statement end ===')")
        writeLn("    else:")
        writeLn("        print(str(scanner_result))")

    def generate(self, writeLn):
        """Generates the parser for an initially given grammar.

        :param writeLn: A function used to write the output.
        """
        # Indent
        S = "    "

        writeLn("################################################################")
        for name, module in self.grammar.imports.items():
            writeLn("import {} as {}".format(module, name))

        # Create parser methods for every non-terminal
        for NT in self.grammar.nonterminals.values():
            writeLn()
            writeLn()
            writeLn(S * 0 + "def {}(token_stream, parse_tree=False):".format(NT.name))
            predicts = {}
            assert len(NT.rules) > 0, "{} has no rules, probably you mixed up tokens and rules".format(NT.name)
            # For every rule use the PREDICT set to decide which tokens to expect.
            for rule in NT.rules:
                PREDICT = self.analysis.PREDICT(rule)
                writeLn(S * 1 + "#  PREDICT({}): {}".format(rule, PREDICT))

                # Make sure that the PREDICT set for all rules of a specific non-terminal is unique.
                # This is necessary because if multiple rules of one non-terminal share the same PREDICT set
                # then we can't decide which rule has been taken (the first? the last? something between?).
                common_predict = PREDICT & predicts.keys()
                if len(common_predict) != 0:
                    msg = "Grammar is not in LL(1): {} does predict:\n".format(common_predict)
                    for lookahead in common_predict:
                        msg += " " + repr(predicts[lookahead]) + "\n"
                    msg += " " + repr(rule) + "\n"
                    raise RuntimeError(msg)

                # Save PREDICT terminals for the upper verification of further non-terminal rules.
                for lookahead in PREDICT:
                    predicts[lookahead] = rule

                # The next token has to be one of our PREDICT terminals.
                writeLn(S * 1 + "if token_stream.peek() in {}:".format([x.name for x in PREDICT]))
                variables = [repr(rule.lhs.name)]
                # Create a variable for every word of the right-hand side of the rule.
                for idx, symbol in enumerate(rule.rhs):
                    name = "var_{}".format(idx)
                    # Read the terminal token by expecting its type.
                    if isinstance(symbol, Terminal):
                        writeLn(S * 2 + "{} = token_stream.read(expected={})".format(name, repr(symbol.name)))
                        variables.append(name)
                    elif isinstance(symbol, Epsilon):
                        writeLn(S * 2 + "# Skip Epsilon")
                    # Non-terminal because a symbol can only be a terminal, a non-terminal or epsilon.
                    # For non-terminals we call the corresponding functions.
                    else:
                        writeLn(S * 2 + "{} = {}(token_stream, parse_tree)".format(name, symbol.name))
                        variables.append(name)
                # If an action has been defined within the grammar definition use that return format
                # if the parse_tree parameter is false.
                if rule.action:
                    action_value = rule.action
                    for idx, value in enumerate(variables):
                        action_value = action_value.replace("${}".format(idx), value)

                    writeLn(S * 2 + "if not parse_tree:")
                    writeLn(S * 2 + "    return {}".format(action_value.strip()))
                # Otherwise simply return all variables as a list.
                parse_tree = "[{}]".format(", ".join(variables))
                writeLn(S * 2 + "return {}".format(parse_tree))
            # Raise an error because if we reach this statement that means that the next token
            # is not one of our predicted terminals of the PREDICT set and this is an error.
            writeLn(S * 1 + "token_stream.raise_error()")

        # Create a parsing method which starts the parsing process by calling the function
        # generated for the start symbol.
        writeLn()
        writeLn()
        writeLn("def parse(text, *args, **kwargs):")
        writeLn("    scanner = Scanner(text)")
        writeLn("    return {}(scanner, *args, **kwargs)".format(self.grammar.start_symbol.name))

        self.__gen_pretty_print__(writeLn)


class ScannerGenerator:
    """Creates a scanner for a given grammar.

    A scanner is an entity which extracts tokens out of a given data stream (for example a text).
    Every parser has a scanner which operates as a token stream to enable the parser
    to work on the data stream token-wise.
    """

    def __init__(self, grammar):
        self.grammar = grammar

    def generate(self, writeLn):
        """Creates a scanner class using the given grammar.

        :param writeLn: A function used to write the output.
        """
        writeLn("################################################################")
        writeLn("from parserll1.scanner import BaseScanner")
        writeLn()
        writeLn()
        writeLn("class Scanner(BaseScanner):")
        writeLn("    scanner_table = [")
        # Create the scanner table by evaluating all terminal expressions of the grammar.
        for T in self.grammar.terminals.values():
            # Test if given regular expression is actually valid.
            try:
                re.compile(T.regex)
            except re.error as e:
                raise RuntimeError("Invalid Token-Rule: " + str(T))
            writeLn("        {},".format(repr((T.name, T.regex, T.skip))))
        writeLn("    ]")
        writeLn()


def _get_grammar_path(grammar_name):
    """Returns the relative path of a grammar file to a given grammar name.

    A grammar may be written as:
    - Python file (.py)
    - Language file (.ll1)

    :param grammar_name: The name of the grammar.
    :return: Relative path to the grammar file, starting at the current directory or None if no grammar exists.
    """
    base_path = os.path.relpath(os.path.dirname(__file__), ".")
    file_path = os.path.join(base_path, "grammars", grammar_name + ".py")
    if os.path.exists(file_path):
        return file_path
    file_path = os.path.join(base_path, "grammars", grammar_name + ".ll1")
    if os.path.exists(file_path):
        return file_path


def _get_parser_directory():
    """Returns the relative path of the parser directory.

    :return: Relative path to the parser file, starting at the current directory.
    """
    base_path = os.path.relpath(os.path.dirname(__file__), ".")
    return os.path.join(base_path, "generated")


def _get_parser_path(grammar_name):
    """Returns the relative file path of a generated parser for the given grammar name.

    :param grammar_name: The name of the grammar.
    :return: Relative path to the parser file, starting at the current directory.
    """
    base, _ = os.path.splitext(grammar_name)
    return os.path.join(_get_parser_directory(), base + ".py")


def _load_module(mod_path):
    """Loads a module by its path.

    :param mod_path: Path to the module.
    """
    logger.debug("Loading Module:    {}".format(mod_path))
    # Remove current directory from module path.
    if mod_path.startswith("./"):
        mod_path = mod_path[2:]
    # Extract the module name from its path.
    # Further remove the last three characters (file ending) from the module path: '.', 'p', 'y'
    mod_name = mod_path.replace("/", ".").replace("\\", ".")[:-3]
    assert os.path.exists(mod_path)
    # Necessary so that the module is noticed by the import system.
    importlib.invalidate_caches()
    module = importlib.import_module(mod_name)
    return module


def load_grammar(grammar_name):
    """Returns the grammar for a given grammar name.

    :param grammar_name: The name of the grammar.
    :return: The grammar of the given grammar name.
    """
    file_path = _get_grammar_path(grammar_name)
    if file_path.endswith(".py"):
        return _load_module(file_path).grammar
    else:
        return parse_grammar(file_path)


def parse_grammar(file_path):
    """Returns a grammar by parsing the grammar defintion under the given file path.

    :param file_path: Path to the grammar to be parsed.
    :return: Grammar of the given grammar definition under file_path.
    """
    # First, we have to build a parser for grammars
    grammar_parser = load_parser("grammarGrammar")

    # Parse the actual grammar
    with open(file_path) as f:
        grammar_parse_tree = grammar_parser.parse(f.read())

    grammar = Grammar()
    for rule in grammar_parse_tree:
        # Setup terminals by using allowed tokens of the grammar.
        if rule[0] == "opt":
            (_, Type, Ident, Arg) = rule
            if Type.load == "%TOKEN":
                grammar.T(Ident.load, eval(Arg))
            elif Type.load == "%IGNORE":
                grammar.T(Ident.load).skip = True
            elif Type.load == "%START":
                grammar.NT(Ident.load, True)
            elif Type.load == "%IMPORT":
                grammar.addImport(Ident.load, eval(Arg))
            else:
                raise RuntimeError("Unknown Optional Argument: " + Type.load)
        # Build up the productions of non-terminals.
        elif rule[0] == "rule":
            (_, lhs, productions) = rule
            # Left-hand side of a production is always a non-terminal.
            lhs = grammar.NT(lhs.load)
            for production in productions[1:]:
                _, word, action = production
                rhs = []
                # Fill up the right-hand side with (non-)terminals.
                for symbol in word[1:]:
                    if symbol == "EPSILON":
                        rhs.append(grammar.E)
                    elif symbol in grammar.terminals:
                        rhs.append(grammar.T(symbol))
                    else:
                        rhs.append(grammar.NT(symbol))
                # If an action is provided use that but remove starting/trailing characters: '{', '}'.
                if action is not None:
                    grammar.addRule(lhs, rhs, action[1:-1])
                elif len(rhs) == 1:
                    grammar.addRule(lhs, rhs, "$1")
                else:
                    raise RuntimeError("Rule has no action: " + rule)

    return grammar


def load_parser(grammar_name, silent=False):
    """Loads a parser for a given grammar name.

    :param grammar_name: The name of the grammar to load a parser for.
    :return: Loaded parser file of the given grammar.
    """
    parser_file_path = _get_parser_path(grammar_name)
    grammar_file_path = _get_grammar_path(grammar_name)
    directory = os.path.dirname(__file__)
    files = [grammar_file_path] + [os.path.join(directory, x) for x in os.listdir(directory)]

    if not grammar_file_path and not os.path.exists(parser_file_path):
        raise RuntimeError("No grammar or parser for {} was found".format(grammar_name))

    # We want to generate a new parser for the given grammar if:
    # - The grammar exists
    # - Currently no parser exists
    # - The files within the directory have been updated and therefore
    #   the existing parser is out-of-date.
    if grammar_file_path and (
        not os.path.exists(parser_file_path)
        or any([os.stat(fn).st_mtime >= os.stat(parser_file_path).st_mtime for fn in files])
    ):
        grammar = load_grammar(grammar_name)
        logger.info("Generating parser: {}".format(parser_file_path))
        try:
            parser_dir = _get_parser_directory()
            pathlib.Path(parser_dir).mkdir(parents=True, exist_ok=True)

            # Pass a write function to the generator classes.
            # Using the write function the generator classes can write directly
            # to the file under the path parser_file_path.
            with open(parser_file_path, "w+") as fd:

                def writeLn(x=""):
                    fd.write(x + "\n")

                ScannerGenerator(grammar).generate(writeLn)
                ParserGenerator(grammar).generate(writeLn)
        except Exception as e:
            os.unlink(parser_file_path)
            raise e

    # After parser generation load the generated parser module.
    return _load_module(parser_file_path)


# When the script itself is executed via a command line call (thus not imported)
# load a parser using the first command line argument.
if __name__ == "__main__":
    parserFn = _get_parser_path(sys.argv[1])
    if os.path.exists(parserFn):
        os.unlink(parserFn)
    parser = load_parser(sys.argv[1])
