import re


class ScannerError(RuntimeError):
    pass


class ParserError(RuntimeError):
    pass


class Token:
    def __init__(self, type, load, line, col):
        self.type = type
        self.load = load
        self.line = line
        self.col = col

    def __repr__(self):
        return "{}({})".format(self.type, self.load)


class BaseScanner:
    def __init__(self, text):
        self.regex = {}
        self.skip = {}
        for token, regex, skip in self.scanner_table:
            self.regex[token] = re.compile(regex, re.M)
            self.skip[token] = skip

        # This scanner is very ineffective and scans the whole text
        # before doing anything else. However, thereby you can look at
        # the token_stream at any given point in time.
        self.token_stream = []

        # Just lex the whole text
        line = 1
        col = 0
        while True:
            token, lexeme = None, ""
            for name, regex in self.regex.items():
                m = regex.match(text)
                if m and (not token or len(m.group(0)) > len(lexeme)):
                    token = name
                    lexeme = m.group(0)
            if token is None:
                msg = "Cannot scan: {}...".format(repr(text[:20]))
                raise ScannerError(msg)

            # Push token to token stream
            if not self.skip[token]:
                self.token_stream.append(Token(token, lexeme, line, col))

            # Consume text
            text = text[len(lexeme) :]
            if "\n" in lexeme:
                line += lexeme.count("\n")
                col = len(lexeme[lexeme.rindex("\n") + 1 :])
            else:
                col += len(lexeme)

            if text == "" and lexeme == "":
                break

    def peek(self):
        return self.token_stream[0].type

    def read(self, expected=None):
        if expected and self.peek() != expected:
            self.raise_error(expected=expected)
        return self.token_stream.pop(0)

    def raise_error(self, expected=None):
        token = self.token_stream.pop(0)
        msg = "Unexpected token: {} (line: {}, col: {})".format(token.type, token.line, token.col)
        if expected:
            msg += ", expected: {}".format(expected)
        raise ParserError(msg)
