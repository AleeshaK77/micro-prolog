from ast import Compound
from unify import unify, apply_subst

def solve_goals(goals, kb, subst=None):

    if subst is None:
        subst = {}

    if not goals:  # Base case: all subgoals in branch are proven
        yield subst
        return

    # 1. Substitute current bindings into the first goal
    first_goal = apply_subst(goals[0], subst)
    rest_goals = goals[1:]

    # 2. Fetch candidate rules from KB with fresh variables
    for rule in kb.fetch_standardized_rules():

        # 3. Unify using the accumulated substitution environment
        new_subst = unify(first_goal, rule.head, subst)

        if new_subst is not None:

            # 4. Prepend rule body to remaining goals and recurse
            new_goals = list(rule.body) + rest_goals
            yield from solve_goals(new_goals, kb, new_subst)

def query(goals, kb):

    if isinstance(goals, Compound):
        goals = [goals]

    for solution_subst in solve_goals(goals, kb):
        cleaned_subst = {}

        for goal in goals:
            for var in _extract_vars(goal):
                cleaned_subst[var] = apply_subst(var, solution_subst)

        yield cleaned_subst

def _extract_vars(term):
    from ast import Var

    if isinstance(term, Var):
        return {term}

    elif isinstance(term, Compound):
        vars_set = set()

        for arg in term.args:
            vars_set.update(_extract_vars(arg))

        return vars_set

    return set()