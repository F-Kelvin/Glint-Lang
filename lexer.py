"""
Lexer for the Glint programming language.

Glint is a small, Turing-incomplete language with:
  - integer and string literals, plus booleans (true / false)
  - variables declared with `var`
  - arithmetic: + - * /
  - string concatenation: .. (kept separate from + on purpose)
  - comparisons: == != < > <= >=
  - `if` / `else` blocks, C-style, with braces and no loops or
    functions, so no Glint program can recurse or iterate --
    every program halts after a bounded number of steps.
  - `say` for printing

Statements end with `;`, blocks use `{ }`, comments start with `//`.
This is a deliberately different shape (symbols, not keyword blocks)
from other BYOL submissions that use newline-terminated statements
closed with a keyword like `end`.

Usage:
    python lexer.py path/to/script.glint
"""

import sys


# ---------------------------------------------------------------------------
# Token vocabulary
# ---------------------------------------------------------------------------

KEYWORDS = {"var", "if", "else", "say", "true", "false"}

# Longest-match-first: multi-character operators must come before any
# single-character operator that is a prefix of them.
OPERATORS = ["==", "!=", "<=", ">=", "..", "+", "-", "*", "/", "=", "<", ">"]

PUNCTUATION = {"(", ")", "{", "}", ";"}

ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}


class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"


class LexError(Exception):
    """Raised when the lexer hits source text it cannot turn into a token.

    Carries line/column so callers can report a clean error instead of a
    raw traceback -- this is the "reject illegal characters gracefully"
    requirement from the rubric.
    """

    def __init__(self, message, line, column):
        super().__init__(f"Lex error at line {line}, column {column}: {message}")
        self.line = line
        self.column = column


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1

    # -- low-level cursor helpers -----------------------------------------

    def peek(self, offset=0):
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def advance(self):
        ch = self.peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def error(self, message):
        raise LexError(message, self.line, self.column)

    # -- main entry point ----------------------------------------------

    def tokenize(self):
        tokens = []
        while True:
            self.skip_whitespace_and_comments()
            ch = self.peek()
            start_line, start_col = self.line, self.column

            if ch is None:
                tokens.append(Token("EOF", None, start_line, start_col))
                break
            elif ch.isdigit():
                tokens.append(self.read_number(start_line, start_col))
            elif ch == '"':
                tokens.append(self.read_string(start_line, start_col))
            elif ch.isalpha() or ch == "_":
                tokens.append(self.read_identifier(start_line, start_col))
            elif ch in PUNCTUATION:
                self.advance()
                tokens.append(Token(ch, ch, start_line, start_col))
            else:
                op = self.match_operator()
                if op is None:
                    self.error(f"illegal character {ch!r}")
                for _ in op:
                    self.advance()
                tokens.append(Token("OP", op, start_line, start_col))

        return tokens

    # -- skipping ---------------------------------------------------------

    def skip_whitespace_and_comments(self):
        while True:
            ch = self.peek()
            if ch is not None and ch.isspace():
                self.advance()
            elif ch == "/" and self.peek(1) == "/":
                while self.peek() is not None and self.peek() != "\n":
                    self.advance()
            else:
                return

    # -- token readers ------------------------------------------------

    def match_operator(self):
        for op in OPERATORS:
            if self.source.startswith(op, self.pos):
                return op
        return None

    def read_number(self, line, col):
        start = self.pos
        while self.peek() is not None and self.peek().isdigit():
            self.advance()
        return Token("INTEGER", int(self.source[start:self.pos]), line, col)

    def read_string(self, line, col):
        self.advance()  # consume opening quote
        chars = []
        while True:
            ch = self.peek()
            if ch is None or ch == "\n":
                self.error("unterminated string literal")
            if ch == '"':
                self.advance()
                break
            if ch == "\\":
                self.advance()
                esc = self.peek()
                if esc not in ESCAPES:
                    self.error(f"invalid escape sequence '\\{esc}'")
                chars.append(ESCAPES[esc])
                self.advance()
            else:
                chars.append(ch)
                self.advance()
        return Token("STRING", "".join(chars), line, col)

    def read_identifier(self, line, col):
        start = self.pos
        while self.peek() is not None and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()
        value = self.source[start:self.pos]
        if value in KEYWORDS:
            return Token(value.upper(), value, line, col)
        return Token("IDENTIFIER", value, line, col)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) != 2:
        print("usage: python lexer.py <source_file.glint>")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        source = f.read()

    lexer = Lexer(source)
    try:
        for tok in lexer.tokenize():
            print(tok)
    except LexError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
