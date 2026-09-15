import re
from ast import Var, Atom, Compound, Rule


class Tokenizer:
    """converts raw string into stream of Prolog tokens."""
    TOKEN_RE = re.compile(
        r'\s*(?:'
        r'(:-)|'                 #rule neck ':-'
        r'([A-Z_][a-zA-Z0-9_]*)|' #variable (capital letter or '_')
        r'([a-z0-9_]+)|'          #atom/functor (lowercase or numbers)
        r'([(),.])'              #punctuation
        r')'
    )

    def __init__(self, text):
        self.tokens = []
        for match in self.TOKEN_RE.finditer(text):
            neck, var, atom, punct = match.groups()
            if neck:
                self.tokens.append(('NECK', neck))
            elif var:
                self.tokens.append(('VAR', var))
            elif atom:
                self.tokens.append(('ATOM', atom))
            elif punct:
                self.tokens.append(('PUNCT', punct))

        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def pop(self):
        tok = self.peek()
        self.pos += 1
        return tok


class PrologParser:
    """parses token stream into AST objects."""

    def __init__(self, text):
        self.tok = Tokenizer(text)

    def parse_term(self):
        kind, val = self.tok.pop()
        if kind == 'VAR':
            return Var(val)
        elif kind == 'ATOM':
            next_kind, next_val = self.tok.peek() #check if atom is compound predicate
            if next_kind == 'PUNCT' and next_val == '(':
                self.tok.pop()  # consume '('
                args = []
                while True:
                    args.append(self.parse_term())
                    pk_kind, pk_val = self.tok.peek()
                    if pk_val == ',':
                        self.tok.pop()  # consume ','
                    elif pk_val == ')':
                        self.tok.pop()  # consume ')'
                        break
                    else:
                        raise SyntaxError(f"Expected ',' or ')' but got '{pk_val}'")
                return Compound(val, *args)
            return Atom(val)
        else:
            raise SyntaxError(f"Unexpected token: {val}")

    def parse_rule_or_query(self):
        """parses full line terminated by period '.'."""
        head = self.parse_term()
        pk_kind, pk_val = self.tok.peek()

        body = []
        if pk_kind == 'NECK':
            self.tok.pop()  #consume ':-'
            while True:
                body.append(self.parse_term())
                next_kind, next_val = self.tok.peek()
                if next_val == ',':
                    self.tok.pop()
                elif next_val == '.':
                    break
                else:
                    raise SyntaxError(f"Expected ',' or '.' in body, got '{next_val}'")

        end_kind, end_val = self.tok.pop()
        if end_val != '.':
            raise SyntaxError(f"Expected '.' at end of statement, got '{end_val}'")

        return Rule(head, *body)


def parse_line(line):
    """util helper to parse single string statement into AST Rule."""
    line = line.strip()
    if not line or line.startswith('%'):
        return None  #skip empty lines/comments
    parser = PrologParser(line)
    return parser.parse_rule_or_query()