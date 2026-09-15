class Term:
    """Base class for all logical terms."""
    pass


class Var(Term): 
    """logical variable (e.g., X, Y, Z)."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name

    def __hash__(self):
        return hash(("Var", self.name))


class Atom(Term):
    """constant value or basic symbol (e.g., alice, bob, 42)."""
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self):
        return hash(("Atom", self.name))


class Compound(Term):
    """predicate or complex term: functor(arg1, arg2, ...)."""
    def __init__(self, functor, *args):
        self.functor = functor
        self.args = tuple(args)  # Tuple ensures immutability for hashing

    def __repr__(self):
        args_str = ", ".join(repr(arg) for arg in self.args)
        return f"{self.functor}({args_str})"

    def __eq__(self, other):
        return (isinstance(other, Compound) and 
                self.functor == other.functor and 
                self.args == other.args)

    def __hash__(self):
        return hash((self.functor, self.args))


class Rule:
    """horn clause: Head :- Body. (Facts have an empty body)."""
    def __init__(self, head, *body):
        self.head = head
        self.body = tuple(body)

    def __repr__(self):
        if not self.body:
            return f"{self.head}."
        body_str = ", ".join(repr(b) for b in self.body)
        return f"{self.head} :- {body_str}."

    def __eq__(self, other):
        return (isinstance(other, Rule) and 
                self.head == other.head and 
                self.body == other.body)

    def __hash__(self):
        return hash((self.head, self.body))
    
