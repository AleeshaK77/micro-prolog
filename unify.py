from ast import Term, Var, Atom, Compound


def apply_subst(term, subst):
    """recursively substitutes variables in a term using the substitution dict theta."""
    if not subst:
        return term

    if isinstance(term, Var):
        if term in subst: return apply_subst(subst[term], subst) #recursively substitute in case variables chain 
        return term

    elif isinstance(term, Atom):
        return term

    elif isinstance(term, Compound):
        new_args = [apply_subst(arg, subst) for arg in term.args]
        return Compound(term.functor, *new_args)

    return term


def occurs_check(var, term, subst):
    """returns True if var occurs anywhere inside term (prevents infinite loops)."""
    term = apply_subst(term, subst)
    if var == term:
        return True
    if isinstance(term, Compound):
        return any(occurs_check(var, arg, subst) for arg in term.args)
    return False


def unify(x, y, subst=None):
    """finds the Most General Unifier (MGU) for terms x and y given an existing substitution environment."""
    if subst is None:
        subst = {}

    if subst is None: #if already failed, return failure
        return None

    x = apply_subst(x, subst) #resolve current variable bindings first
    y = apply_subst(y, subst)

    if x == y: #identical terms unify with no changes
        return subst

    if isinstance(x, Var): #variable cases
        return unify_var(x, y, subst)
    if isinstance(y, Var):
        return unify_var(y, x, subst)

    if isinstance(x, Compound) and isinstance(y, Compound): #compound terms unify if functors match and all args unify
        if x.functor != y.functor or len(x.args) != len(y.args):
            return None

        current_subst = dict(subst)
        for arg1, arg2 in zip(x.args, y.args):
            current_subst = unify(arg1, arg2, current_subst)
            if current_subst is None:
                return None
        return current_subst

    return None #non-identical atoms fail


def unify_var(var, x, subst):
    """helper function to handle variable bindings with optional occurs check."""
    if var in subst:
        return unify(subst[var], x, subst)
    if x in subst:
        return unify(var, subst[x], subst)

    if occurs_check(var, x, subst): #occurs check: prevents infinite structural loops
        return None

    new_subst = dict(subst)
    new_subst[var] = x
    return new_subst