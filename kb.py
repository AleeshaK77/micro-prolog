from ast import Var, Atom, Compound, Rule


def standardize_variables(rule, counter=0):
    """renames all vars in rule with unique suffixes."""
    var_map = {}

    def rename(term):
        if isinstance(term, Var):
            if term not in var_map:
                var_map[term] = Var(f"{term.name}_{counter}")
            return var_map[term]
        elif isinstance(term, Atom):
            return term
        elif isinstance(term, Compound):
            return Compound(term.functor, *[rename(arg) for arg in term.args])
        return term

    new_head = rename(rule.head)
    new_body = [rename(b) for b in rule.body]
    return Rule(new_head, *new_body), counter + 1


class KnowledgeBase:
    """stores facts and rules and retrieves them for unification."""
    def __init__(self):
        self.rules = []
        self._counter = 0

    def tell(self, rule):
        """adds fact or rule to the knowledge base."""
        self.rules.append(rule)

    def fetch_standardized_rules(self):
        """yields rules from KB with variables standardized apart."""
        for rule in self.rules:
            standardized_rule, self._counter = standardize_variables(rule, self._counter)
            yield standardized_rule
