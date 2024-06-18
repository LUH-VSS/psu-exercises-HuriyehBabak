################################################################
from parserll1.scanner import BaseScanner


class Scanner(BaseScanner):
    scanner_table = [
        ("EOF", "$", False),
        ("WS", "[\n\t ]+", True),
        ("COMMENT", "//.*$", True),
        ("VAR", "var", False),
        ("FUNC", "func", False),
        ("IF", "if", False),
        ("ELSE", "else", False),
        ("WHILE", "while", False),
        ("RETURN", "return", False),
        ("BREAK", "break", False),
        ("CONTINUE", "continue", False),
        ("FOR", "for", False),
        ("LPAR", "\\(", False),
        ("RPAR", "\\)", False),
        ("LBRACE", "{", False),
        ("RBRACE", "}", False),
        ("ASSIGN", ":=", False),
        ("COLON", ":", False),
        ("SEMICOLON", ";", False),
        ("COMMA", ",", False),
        ("ET", "&", False),
        ("NOT", "!", False),
        ("LE", "<=", False),
        ("EQ", "==", False),
        ("GE", ">=", False),
        ("INT", "int", False),
        ("IDENT", "[a-zA-Z_][a-zA-Z0-9_]*", False),
        ("LITERAL", "[0-9]+", False),
        ("ADD", "[+]", False),
        ("SUB", "-", False),
        ("MUL", "[*]", False),
        ("DIV", "/", False),
    ]


################################################################
import AST.types as T


def program(token_stream, parse_tree=False):
    #  PREDICT(NT(program) -> [NT(decl_list), T(EOF)]): {T(EOF), T(FUNC)}
    if token_stream.peek() in ["EOF", "FUNC"]:
        var_0 = decl_list(token_stream, parse_tree)
        var_1 = token_stream.read(expected="EOF")
        if not parse_tree:
            return T.TranslationUnitDecl(decls=var_0)
        return ["program", var_0, var_1]
    token_stream.raise_error()


def type(token_stream, parse_tree=False):
    #  PREDICT(NT(type) -> [T(INT)]): {T(INT)}
    if token_stream.peek() in ["INT"]:
        var_0 = token_stream.read(expected="INT")
        if not parse_tree:
            return T.TypeInt()
        return ["type", var_0]
    #  PREDICT(NT(type) -> [T(ET), NT(type)]): {T(ET)}
    if token_stream.peek() in ["ET"]:
        var_0 = token_stream.read(expected="ET")
        var_1 = type(token_stream, parse_tree)
        if not parse_tree:
            return T.TypePointer(var_1)
        return ["type", var_0, var_1]
    token_stream.raise_error()


def decl_list(token_stream, parse_tree=False):
    #  PREDICT(NT(decl_list) -> [NT(func_decl), NT(decl_list)]): {T(FUNC)}
    if token_stream.peek() in ["FUNC"]:
        var_0 = func_decl(token_stream, parse_tree)
        var_1 = decl_list(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["decl_list", var_0, var_1]
    #  PREDICT(NT(decl_list) -> [E]): {T(EOF)}
    if token_stream.peek() in ["EOF"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["decl_list"]
    token_stream.raise_error()


def identifier(token_stream, parse_tree=False):
    #  PREDICT(NT(identifier) -> [T(IDENT)]): {T(IDENT)}
    if token_stream.peek() in ["IDENT"]:
        var_0 = token_stream.read(expected="IDENT")
        if not parse_tree:
            return T.Identifier(var_0.load)
        return ["identifier", var_0]
    token_stream.raise_error()


def literal(token_stream, parse_tree=False):
    #  PREDICT(NT(literal) -> [T(LITERAL)]): {T(LITERAL)}
    if token_stream.peek() in ["LITERAL"]:
        var_0 = token_stream.read(expected="LITERAL")
        if not parse_tree:
            return T.Literal(int(var_0.load))
        return ["literal", var_0]
    token_stream.raise_error()


def func_decl(token_stream, parse_tree=False):
    #  PREDICT(NT(func_decl) -> [T(FUNC), NT(identifier), T(LPAR), NT(param_list), T(RPAR), T(COLON), NT(type), NT(block)]): {T(FUNC)}
    if token_stream.peek() in ["FUNC"]:
        var_0 = token_stream.read(expected="FUNC")
        var_1 = identifier(token_stream, parse_tree)
        var_2 = token_stream.read(expected="LPAR")
        var_3 = param_list(token_stream, parse_tree)
        var_4 = token_stream.read(expected="RPAR")
        var_5 = token_stream.read(expected="COLON")
        var_6 = type(token_stream, parse_tree)
        var_7 = block(token_stream, parse_tree)
        if not parse_tree:
            return T.FuncDecl(name=var_1.name, params=var_3, return_type=var_6, statements=var_7.statements)
        return ["func_decl", var_0, var_1, var_2, var_3, var_4, var_5, var_6, var_7]
    token_stream.raise_error()


def param_list(token_stream, parse_tree=False):
    #  PREDICT(NT(param_list) -> [NT(param), NT(param_list_tail)]): {T(IDENT)}
    if token_stream.peek() in ["IDENT"]:
        var_0 = param(token_stream, parse_tree)
        var_1 = param_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["param_list", var_0, var_1]
    #  PREDICT(NT(param_list) -> [E]): {T(RPAR)}
    if token_stream.peek() in ["RPAR"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["param_list"]
    token_stream.raise_error()


def block(token_stream, parse_tree=False):
    #  PREDICT(NT(block) -> [T(LBRACE), NT(stmt_list), T(RBRACE)]): {T(LBRACE)}
    if token_stream.peek() in ["LBRACE"]:
        var_0 = token_stream.read(expected="LBRACE")
        var_1 = stmt_list(token_stream, parse_tree)
        var_2 = token_stream.read(expected="RBRACE")
        if not parse_tree:
            return T.CodeBlock(var_1)
        return ["block", var_0, var_1, var_2]
    token_stream.raise_error()


def param(token_stream, parse_tree=False):
    #  PREDICT(NT(param) -> [NT(identifier), T(COLON), NT(type)]): {T(IDENT)}
    if token_stream.peek() in ["IDENT"]:
        var_0 = identifier(token_stream, parse_tree)
        var_1 = token_stream.read(expected="COLON")
        var_2 = type(token_stream, parse_tree)
        if not parse_tree:
            return T.VarDecl(name=var_0.name, type=var_2)
        return ["param", var_0, var_1, var_2]
    token_stream.raise_error()


def param_list_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(param_list_tail) -> [T(COMMA), NT(param), NT(param_list_tail)]): {T(COMMA)}
    if token_stream.peek() in ["COMMA"]:
        var_0 = token_stream.read(expected="COMMA")
        var_1 = param(token_stream, parse_tree)
        var_2 = param_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_1] + var_2
        return ["param_list_tail", var_0, var_1, var_2]
    #  PREDICT(NT(param_list_tail) -> [E]): {T(RPAR)}
    if token_stream.peek() in ["RPAR"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["param_list_tail"]
    token_stream.raise_error()


def stmt_list(token_stream, parse_tree=False):
    #  PREDICT(NT(stmt_list) -> [NT(stmt), NT(stmt_list)]): {T(NOT), T(MUL), T(SUB), T(RETURN), T(FOR), T(CONTINUE), T(VAR), T(ET), T(WHILE), T(LITERAL), T(BREAK), T(LPAR), T(IDENT), T(IF)}
    if token_stream.peek() in [
        "NOT",
        "MUL",
        "SUB",
        "RETURN",
        "FOR",
        "CONTINUE",
        "VAR",
        "ET",
        "WHILE",
        "LITERAL",
        "BREAK",
        "LPAR",
        "IDENT",
        "IF",
    ]:
        var_0 = stmt(token_stream, parse_tree)
        var_1 = stmt_list(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["stmt_list", var_0, var_1]
    #  PREDICT(NT(stmt_list) -> [E]): {T(RBRACE)}
    if token_stream.peek() in ["RBRACE"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["stmt_list"]
    token_stream.raise_error()


def stmt(token_stream, parse_tree=False):
    #  PREDICT(NT(stmt) -> [NT(var_decl)]): {T(VAR)}
    if token_stream.peek() in ["VAR"]:
        var_0 = var_decl(token_stream, parse_tree)
        if not parse_tree:
            return var_0
        return ["stmt", var_0]
    #  PREDICT(NT(stmt) -> [NT(expr), T(SEMICOLON)]): {T(NOT), T(LITERAL), T(MUL), T(SUB), T(LPAR), T(ET), T(IDENT)}
    if token_stream.peek() in ["NOT", "LITERAL", "MUL", "SUB", "LPAR", "ET", "IDENT"]:
        var_0 = expr(token_stream, parse_tree)
        var_1 = token_stream.read(expected="SEMICOLON")
        if not parse_tree:
            return var_0
        return ["stmt", var_0, var_1]
    #  PREDICT(NT(stmt) -> [T(RETURN), NT(expr), T(SEMICOLON)]): {T(RETURN)}
    if token_stream.peek() in ["RETURN"]:
        var_0 = token_stream.read(expected="RETURN")
        var_1 = expr(token_stream, parse_tree)
        var_2 = token_stream.read(expected="SEMICOLON")
        if not parse_tree:
            return T.ReturnStmt(expr=var_1)
        return ["stmt", var_0, var_1, var_2]
    #  PREDICT(NT(stmt) -> [T(IF), T(LPAR), NT(expr), T(RPAR), NT(block), NT(if_tail)]): {T(IF)}
    if token_stream.peek() in ["IF"]:
        var_0 = token_stream.read(expected="IF")
        var_1 = token_stream.read(expected="LPAR")
        var_2 = expr(token_stream, parse_tree)
        var_3 = token_stream.read(expected="RPAR")
        var_4 = block(token_stream, parse_tree)
        var_5 = if_tail(token_stream, parse_tree)
        if not parse_tree:
            return T.IfStmt(cond=var_2, then_block=var_4, else_block=var_5)
        return ["stmt", var_0, var_1, var_2, var_3, var_4, var_5]
    #  PREDICT(NT(stmt) -> [T(WHILE), T(LPAR), NT(expr), T(RPAR), NT(block)]): {T(WHILE)}
    if token_stream.peek() in ["WHILE"]:
        var_0 = token_stream.read(expected="WHILE")
        var_1 = token_stream.read(expected="LPAR")
        var_2 = expr(token_stream, parse_tree)
        var_3 = token_stream.read(expected="RPAR")
        var_4 = block(token_stream, parse_tree)
        if not parse_tree:
            return T.WhileStmt(cond=var_2, body=var_4)
        return ["stmt", var_0, var_1, var_2, var_3, var_4]
    #  PREDICT(NT(stmt) -> [T(FOR), T(LPAR), NT(expr), T(SEMICOLON), NT(expr), T(SEMICOLON), NT(expr), T(RPAR), NT(block)]): {T(FOR)}
    if token_stream.peek() in ["FOR"]:
        var_0 = token_stream.read(expected="FOR")
        var_1 = token_stream.read(expected="LPAR")
        var_2 = expr(token_stream, parse_tree)
        var_3 = token_stream.read(expected="SEMICOLON")
        var_4 = expr(token_stream, parse_tree)
        var_5 = token_stream.read(expected="SEMICOLON")
        var_6 = expr(token_stream, parse_tree)
        var_7 = token_stream.read(expected="RPAR")
        var_8 = block(token_stream, parse_tree)
        if not parse_tree:
            return T.ForStmt(init=var_2, cond=var_4, next=var_6, body=var_8)
        return ["stmt", var_0, var_1, var_2, var_3, var_4, var_5, var_6, var_7, var_8]
    #  PREDICT(NT(stmt) -> [T(BREAK), T(SEMICOLON)]): {T(BREAK)}
    if token_stream.peek() in ["BREAK"]:
        var_0 = token_stream.read(expected="BREAK")
        var_1 = token_stream.read(expected="SEMICOLON")
        if not parse_tree:
            return T.BreakStmt()
        return ["stmt", var_0, var_1]
    #  PREDICT(NT(stmt) -> [T(CONTINUE), T(SEMICOLON)]): {T(CONTINUE)}
    if token_stream.peek() in ["CONTINUE"]:
        var_0 = token_stream.read(expected="CONTINUE")
        var_1 = token_stream.read(expected="SEMICOLON")
        if not parse_tree:
            return T.ContinueStmt()
        return ["stmt", var_0, var_1]
    token_stream.raise_error()


def var_decl(token_stream, parse_tree=False):
    #  PREDICT(NT(var_decl) -> [T(VAR), NT(identifier), T(COLON), NT(type), T(SEMICOLON)]): {T(VAR)}
    if token_stream.peek() in ["VAR"]:
        var_0 = token_stream.read(expected="VAR")
        var_1 = identifier(token_stream, parse_tree)
        var_2 = token_stream.read(expected="COLON")
        var_3 = type(token_stream, parse_tree)
        var_4 = token_stream.read(expected="SEMICOLON")
        if not parse_tree:
            return T.VarDecl(name=var_1.name, type=var_3)
        return ["var_decl", var_0, var_1, var_2, var_3, var_4]
    token_stream.raise_error()


def expr(token_stream, parse_tree=False):
    #  PREDICT(NT(expr) -> [NT(term), NT(expr_tail)]): {T(NOT), T(LITERAL), T(MUL), T(SUB), T(LPAR), T(ET), T(IDENT)}
    if token_stream.peek() in ["NOT", "LITERAL", "MUL", "SUB", "LPAR", "ET", "IDENT"]:
        var_0 = term(token_stream, parse_tree)
        var_1 = expr_tail(token_stream, parse_tree)
        if not parse_tree:
            return var_1(var_0)
        return ["expr", var_0, var_1]
    token_stream.raise_error()


def if_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(if_tail) -> [E]): {T(NOT), T(MUL), T(SUB), T(RETURN), T(FOR), T(CONTINUE), T(VAR), T(ET), T(WHILE), T(LITERAL), T(BREAK), T(LPAR), T(RBRACE), T(IDENT), T(IF)}
    if token_stream.peek() in [
        "NOT",
        "MUL",
        "SUB",
        "RETURN",
        "FOR",
        "CONTINUE",
        "VAR",
        "ET",
        "WHILE",
        "LITERAL",
        "BREAK",
        "LPAR",
        "RBRACE",
        "IDENT",
        "IF",
    ]:
        # Skip Epsilon
        if not parse_tree:
            return None
        return ["if_tail"]
    #  PREDICT(NT(if_tail) -> [T(ELSE), NT(block)]): {T(ELSE)}
    if token_stream.peek() in ["ELSE"]:
        var_0 = token_stream.read(expected="ELSE")
        var_1 = block(token_stream, parse_tree)
        if not parse_tree:
            return var_1
        return ["if_tail", var_0, var_1]
    token_stream.raise_error()


def term(token_stream, parse_tree=False):
    #  PREDICT(NT(term) -> [NT(factor), NT(term_tail)]): {T(NOT), T(LITERAL), T(MUL), T(SUB), T(LPAR), T(ET), T(IDENT)}
    if token_stream.peek() in ["NOT", "LITERAL", "MUL", "SUB", "LPAR", "ET", "IDENT"]:
        var_0 = factor(token_stream, parse_tree)
        var_1 = term_tail(token_stream, parse_tree)
        if not parse_tree:
            return var_1(var_0)
        return ["term", var_0, var_1]
    token_stream.raise_error()


def expr_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(expr_tail) -> [E]): {T(RPAR), T(SEMICOLON), T(COMMA)}
    if token_stream.peek() in ["RPAR", "SEMICOLON", "COMMA"]:
        # Skip Epsilon
        if not parse_tree:
            return lambda x: x
        return ["expr_tail"]
    #  PREDICT(NT(expr_tail) -> [T(ADD), NT(term), NT(expr_tail)]): {T(ADD)}
    if token_stream.peek() in ["ADD"]:
        var_0 = token_stream.read(expected="ADD")
        var_1 = term(token_stream, parse_tree)
        var_2 = expr_tail(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: var_2(T.Add(lhs=x, rhs=var_1))
        return ["expr_tail", var_0, var_1, var_2]
    #  PREDICT(NT(expr_tail) -> [T(SUB), NT(term), NT(expr_tail)]): {T(SUB)}
    if token_stream.peek() in ["SUB"]:
        var_0 = token_stream.read(expected="SUB")
        var_1 = term(token_stream, parse_tree)
        var_2 = expr_tail(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: var_2(T.Sub(lhs=x, rhs=var_1))
        return ["expr_tail", var_0, var_1, var_2]
    #  PREDICT(NT(expr_tail) -> [T(ASSIGN), NT(expr)]): {T(ASSIGN)}
    if token_stream.peek() in ["ASSIGN"]:
        var_0 = token_stream.read(expected="ASSIGN")
        var_1 = expr(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: T.Assign(lhs=x, rhs=var_1)
        return ["expr_tail", var_0, var_1]
    #  PREDICT(NT(expr_tail) -> [NT(bool_expr_tail)]): {T(LE), T(GE), T(EQ)}
    if token_stream.peek() in ["LE", "GE", "EQ"]:
        var_0 = bool_expr_tail(token_stream, parse_tree)
        if not parse_tree:
            return var_0
        return ["expr_tail", var_0]
    token_stream.raise_error()


def bool_expr_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(bool_expr_tail) -> [T(LE), NT(expr)]): {T(LE)}
    if token_stream.peek() in ["LE"]:
        var_0 = token_stream.read(expected="LE")
        var_1 = expr(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: T.LessEqual(lhs=x, rhs=var_1)
        return ["bool_expr_tail", var_0, var_1]
    #  PREDICT(NT(bool_expr_tail) -> [T(GE), NT(expr)]): {T(GE)}
    if token_stream.peek() in ["GE"]:
        var_0 = token_stream.read(expected="GE")
        var_1 = expr(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: T.LessEqual(lhs=var_1, rhs=x)
        return ["bool_expr_tail", var_0, var_1]
    #  PREDICT(NT(bool_expr_tail) -> [T(EQ), NT(expr)]): {T(EQ)}
    if token_stream.peek() in ["EQ"]:
        var_0 = token_stream.read(expected="EQ")
        var_1 = expr(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: T.Mul(T.LessEqual(lhs=x, rhs=var_1), T.LessEqual(lhs=var_1, rhs=x))
        return ["bool_expr_tail", var_0, var_1]
    token_stream.raise_error()


def factor(token_stream, parse_tree=False):
    #  PREDICT(NT(factor) -> [NT(literal)]): {T(LITERAL)}
    if token_stream.peek() in ["LITERAL"]:
        var_0 = literal(token_stream, parse_tree)
        if not parse_tree:
            return var_0
        return ["factor", var_0]
    #  PREDICT(NT(factor) -> [NT(identifier), NT(factor_tail)]): {T(IDENT)}
    if token_stream.peek() in ["IDENT"]:
        var_0 = identifier(token_stream, parse_tree)
        var_1 = factor_tail(token_stream, parse_tree)
        if not parse_tree:
            return var_1(var_0)
        return ["factor", var_0, var_1]
    #  PREDICT(NT(factor) -> [T(NOT), NT(factor)]): {T(NOT)}
    if token_stream.peek() in ["NOT"]:
        var_0 = token_stream.read(expected="NOT")
        var_1 = factor(token_stream, parse_tree)
        if not parse_tree:
            return T.Not(var_1)
        return ["factor", var_0, var_1]
    #  PREDICT(NT(factor) -> [T(SUB), NT(factor)]): {T(SUB)}
    if token_stream.peek() in ["SUB"]:
        var_0 = token_stream.read(expected="SUB")
        var_1 = factor(token_stream, parse_tree)
        if not parse_tree:
            return T.Neg(var_1)
        return ["factor", var_0, var_1]
    #  PREDICT(NT(factor) -> [T(MUL), NT(factor)]): {T(MUL)}
    if token_stream.peek() in ["MUL"]:
        var_0 = token_stream.read(expected="MUL")
        var_1 = factor(token_stream, parse_tree)
        if not parse_tree:
            return T.Deref(var_1)
        return ["factor", var_0, var_1]
    #  PREDICT(NT(factor) -> [T(ET), NT(factor)]): {T(ET)}
    if token_stream.peek() in ["ET"]:
        var_0 = token_stream.read(expected="ET")
        var_1 = factor(token_stream, parse_tree)
        if not parse_tree:
            return T.Ref(var_1)
        return ["factor", var_0, var_1]
    #  PREDICT(NT(factor) -> [T(LPAR), NT(expr), T(RPAR)]): {T(LPAR)}
    if token_stream.peek() in ["LPAR"]:
        var_0 = token_stream.read(expected="LPAR")
        var_1 = expr(token_stream, parse_tree)
        var_2 = token_stream.read(expected="RPAR")
        if not parse_tree:
            return var_1
        return ["factor", var_0, var_1, var_2]
    token_stream.raise_error()


def term_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(term_tail) -> [T(MUL), NT(factor), NT(term_tail)]): {T(MUL)}
    if token_stream.peek() in ["MUL"]:
        var_0 = token_stream.read(expected="MUL")
        var_1 = factor(token_stream, parse_tree)
        var_2 = term_tail(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: var_2(T.Mul(lhs=x, rhs=var_1))
        return ["term_tail", var_0, var_1, var_2]
    #  PREDICT(NT(term_tail) -> [T(DIV), NT(factor), NT(term_tail)]): {T(DIV)}
    if token_stream.peek() in ["DIV"]:
        var_0 = token_stream.read(expected="DIV")
        var_1 = factor(token_stream, parse_tree)
        var_2 = term_tail(token_stream, parse_tree)
        if not parse_tree:
            return lambda x: var_2(T.Div(lhs=x, rhs=var_1))
        return ["term_tail", var_0, var_1, var_2]
    #  PREDICT(NT(term_tail) -> [E]): {T(SUB), T(GE), T(ADD), T(RPAR), T(EQ), T(ASSIGN), T(COMMA), T(LE), T(SEMICOLON)}
    if token_stream.peek() in ["SUB", "GE", "ADD", "RPAR", "EQ", "ASSIGN", "COMMA", "LE", "SEMICOLON"]:
        # Skip Epsilon
        if not parse_tree:
            return lambda x: x
        return ["term_tail"]
    token_stream.raise_error()


def factor_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(factor_tail) -> [T(LPAR), NT(arg_list), T(RPAR)]): {T(LPAR)}
    if token_stream.peek() in ["LPAR"]:
        var_0 = token_stream.read(expected="LPAR")
        var_1 = arg_list(token_stream, parse_tree)
        var_2 = token_stream.read(expected="RPAR")
        if not parse_tree:
            return lambda x: T.CallExpr(callee=x, arguments=var_1)
        return ["factor_tail", var_0, var_1, var_2]
    #  PREDICT(NT(factor_tail) -> [E]): {T(MUL), T(SUB), T(GE), T(ADD), T(RPAR), T(EQ), T(ASSIGN), T(COMMA), T(DIV), T(LE), T(SEMICOLON)}
    if token_stream.peek() in ["MUL", "SUB", "GE", "ADD", "RPAR", "EQ", "ASSIGN", "COMMA", "DIV", "LE", "SEMICOLON"]:
        # Skip Epsilon
        if not parse_tree:
            return lambda x: x
        return ["factor_tail"]
    token_stream.raise_error()


def arg_list(token_stream, parse_tree=False):
    #  PREDICT(NT(arg_list) -> [NT(expr), NT(arg_list_tail)]): {T(NOT), T(LITERAL), T(MUL), T(SUB), T(LPAR), T(ET), T(IDENT)}
    if token_stream.peek() in ["NOT", "LITERAL", "MUL", "SUB", "LPAR", "ET", "IDENT"]:
        var_0 = expr(token_stream, parse_tree)
        var_1 = arg_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_0] + var_1
        return ["arg_list", var_0, var_1]
    #  PREDICT(NT(arg_list) -> [E]): {T(RPAR)}
    if token_stream.peek() in ["RPAR"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["arg_list"]
    token_stream.raise_error()


def arg_list_tail(token_stream, parse_tree=False):
    #  PREDICT(NT(arg_list_tail) -> [T(COMMA), NT(expr), NT(arg_list_tail)]): {T(COMMA)}
    if token_stream.peek() in ["COMMA"]:
        var_0 = token_stream.read(expected="COMMA")
        var_1 = expr(token_stream, parse_tree)
        var_2 = arg_list_tail(token_stream, parse_tree)
        if not parse_tree:
            return [var_1] + var_2
        return ["arg_list_tail", var_0, var_1, var_2]
    #  PREDICT(NT(arg_list_tail) -> [E]): {T(RPAR)}
    if token_stream.peek() in ["RPAR"]:
        # Skip Epsilon
        if not parse_tree:
            return []
        return ["arg_list_tail"]
    token_stream.raise_error()


def parse(text, *args, **kwargs):
    scanner = Scanner(text)
    return program(scanner, *args, **kwargs)


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
    scanner_result = program(scanner, *args, **kwargs)

    if builtins.type(scanner_result) == list:
        print("=== Parsed statement start ===")
        __print_instruction_plane__(scanner_result)
        print("=== Parsed statement end ===")
    else:
        print(str(scanner_result))
