# Micro-Prolog: Unification and Backward-Chaining Inference

This project implements a small Prolog interpreter in Python based on the logic-programming concepts presented in **Chapter 9 of *Artificial Intelligence: A Modern Approach*** by Stuart Russell and Peter Norvig. The implementation focuses on the core mechanisms underlying first-order logic inference: term representation, substitution, unification, standardization apart, and backward chaining with depth-first backtracking.

The objective is to provide a transparent implementation of these mechanisms rather than a complete Prolog system. The interpreter supports Prolog-style facts and Horn clauses, an interactive REPL, and knowledge-base queries with variable bindings.

---

## Project Architecture

| Module      | Responsibility                                                       |
| :---------- | :------------------------------------------------------------------- |
| `ast.py`    | Representation of variables, atoms, compound terms, and Horn clauses |
| `unify.py`  | Substitution, occurs check, and unification                          |
| `kb.py`     | Knowledge-base storage and standardization apart                     |
| `solver.py` | Backward-chaining inference and depth-first backtracking             |
| `parser.py` | Tokenization and parsing of Prolog-style syntax                      |
| `main.py`   | Knowledge-base loading and interactive REPL                          |

---

## Theoretical Background

### First-Order Logic and Horn Clauses

The interpreter operates on a restricted fragment of **first-order logic** consisting of Horn clauses. A Horn clause contains at most one positive literal and can be written in Prolog as

$$
H \; \mathbin{:-} \; B_1, B_2, \ldots, B_n.
$$

where $H$ is the **head** and $B_1,\ldots,B_n$ form the **body**.

For example,

```prolog
grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
```

represents the logical implication

$$
parent(X,Y) \land parent(Y,Z)
\;\Rightarrow\;
grandparent(X,Z).
$$

A fact is simply a Horn clause with an empty body:

```prolog
parent(alice, bob).
```

The knowledge base therefore defines a collection of logical implications from which the interpreter attempts to establish queries.

---

### Terms

The interpreter represents first-order terms using three fundamental types.

**Variables** represent unknown values:

```prolog
X
Y
```

**Atoms** represent constants:

```prolog
alice
bob
```

**Compound terms** consist of a functor together with zero or more arguments:

```prolog
parent(alice, bob)
```

which can be represented as

$$
parent(alice,bob).
$$

A compound term is structurally determined by both its functor and its arguments. Consequently,

$$
parent(alice,bob) \neq parent(alice,charlie).
$$

This recursive term structure is what allows unification to operate over arbitrary logical expressions.

---

### Substitution

A **substitution** is a mapping from variables to terms. For example,

$$
\theta = \{X \mapsto alice,\;Y \mapsto bob\}.
$$

Applying $\theta$ to

$$
parent(X,Y)
$$

produces

$$
parent(alice,bob).
$$

Substitutions may also contain chains of variable bindings. For example,

$$
\theta = \{X \mapsto Y,\;Y \mapsto bob\}
$$

requires recursive substitution to obtain

$$
X\theta = bob.
$$

The implementation therefore recursively resolves variables when applying substitutions.

---

### Unification

**Unification** is the process of finding a substitution that makes two terms syntactically identical. The result is called a **unifier**.

For example,

$$
parent(alice,X)
$$

and

$$
parent(alice,bob)
$$

can be unified using

$$
\theta = \{X \mapsto bob\}.
$$

After applying $\theta$ to both terms,

$$
parent(alice,X)\theta
=
parent(alice,bob)
$$

and therefore the terms are identical.

The implementation recursively decomposes compound terms. Two compound terms can unify only when:

1. Their functors are identical.
2. They have the same number of arguments.
3. Every corresponding pair of arguments can be unified.

For example,

$$
f(X,g(Y))
$$

and

$$
f(a,g(b))
$$

produce

$$
\theta = \{X \mapsto a,\;Y \mapsto b\}.
$$

If the functors differ,

$$
f(X) \quad\text{and}\quad g(X),
$$

unification fails immediately.

---

### Most General Unifier

Among all possible unifiers, the interpreter seeks a **Most General Unifier (MGU)**: a substitution that imposes no more constraints than necessary.

For example,

$$
parent(alice,X)
$$

and

$$
parent(alice,bob)
$$

have the MGU

$$
\{X \mapsto bob\}.
$$

A more specific substitution such as

$$
\{X \mapsto bob,\;Y \mapsto charlie\}
$$

would also unify the terms if $Y$ were present elsewhere, but would unnecessarily constrain variables unrelated to the unification problem.

The MGU is essential to logic programming because it allows a single inference step to preserve as much generality as possible.

---

### Occurs Check

When unifying a variable with a compound term, the implementation performs an **occurs check** to prevent circular substitutions.

For example,

$$
X = f(X)
$$

cannot produce a valid finite substitution. Attempting to bind

$$
X \mapsto f(X)
$$

would cause recursive substitution to expand indefinitely.

The occurs check therefore rejects the unification whenever the variable already occurs within the term to which it would be bound.

---

### Standardization Apart

Rules are repeatedly reused during inference. Their variables must therefore be renamed each time a rule is considered so that different invocations do not accidentally share variables.

Consider:

```prolog
parent(X, Y) :- ...
```

Two applications of this rule are conceptually independent. The interpreter therefore transforms them internally into something analogous to

```text
parent(X_0, Y_0) :- ...
parent(X_1, Y_1) :- ...
```

This process is called **standardization apart**.

Without it, bindings created while solving one branch of the search could incorrectly affect another branch.

The knowledge base maintains a counter to generate fresh variable names whenever rules are retrieved for inference.

---

### Backward Chaining

The interpreter uses **backward chaining** to answer queries.

Rather than deriving every consequence of the knowledge base in advance, backward chaining starts with a desired goal and asks what would be sufficient to prove it.

For the query

```prolog
grandparent(alice, X).
```

and the rule

```prolog
grandparent(A, C) :- parent(A, B), parent(B, C).
```

the solver first unifies the query with the rule head:

$$
grandparent(alice,X)
$$

with

$$
grandparent(A,C).
$$

This produces bindings equivalent to

$$
A \mapsto alice,\qquad C \mapsto X.
$$

The original goal is then replaced by the rule body:

```prolog
parent(alice, B), parent(B, X).
```

The solver recursively attempts to establish these new goals.

Thus inference proceeds from the desired conclusion toward the facts required to establish it.

---

### Depth-First Search and Backtracking

When multiple rules or facts can satisfy a goal, the interpreter explores them using **depth-first search**.

Suppose the knowledge base contains:

```prolog
parent(alice, bob).
parent(alice, diana).
```

The query

```prolog
parent(alice, X).
```

has two solutions:

$$
X = bob
$$

and

$$
X = diana.
$$

The solver explores one successful branch, returns its substitution, and then backtracks to the previous choice point when the user requests another solution.

This gives the inference process the structure of a depth-first search tree:

```text
                 parent(alice, X)
                  /            \
             X = bob        X = diana
```

If a branch eventually fails, the solver backtracks to the most recent unresolved choice and continues searching.

---

### Inference Procedure

For a list of goals

$$
G_1,G_2,\ldots,G_n,
$$

the solver selects the first goal $G_1$ and considers each standardized rule whose head can unify with it.

For a compatible rule

$$
H \mathbin{:-} B_1,\ldots,B_k,
$$

the solver computes a unifier

$$
\theta = MGU(G_1,H)
$$

and replaces the current goal with

$$
B_1,\ldots,B_k,G_2,\ldots,G_n.
$$

The substitution is propagated through the resulting goals, and the process continues recursively.

The base case occurs when no goals remain:

$$
[].
$$

At that point, every goal in the branch has been established and the accumulated substitution represents a successful solution.

If no rule can unify with the selected goal, that branch fails and the solver backtracks.

---

### Soundness and Completeness

For the restricted Horn-clause language implemented here, the inference procedure follows the standard semantics of SLD-style resolution.

**Soundness.** A successful derivation corresponds to a logical consequence of the Horn-clause knowledge base. The solver therefore does not intentionally produce bindings that cannot be justified by the supplied facts and rules.

**Completeness.** Given a finite search space, depth-first backward chaining can find every logically derivable solution provided that the search eventually explores the corresponding branches. In practice, unrestricted recursive rules can produce infinite branches, so termination is not guaranteed.

For example, a recursive rule such as

```prolog
ancestor(X, Y) :- ancestor(X, Z), parent(Z, Y).
```

can create an infinite search path depending on the ordering of rules and goals. Thus logical completeness does not imply that every query terminates under depth-first evaluation.

---

## Example Knowledge Base

A simple family relationship knowledge base can be written as:

```prolog
parent(alice, bob).
parent(bob, charlie).
parent(alice, diana).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
```

The query

```prolog
?- parent(alice, X).
```

produces:

```text
X = bob ; X = diana.
```

The query

```prolog
?- grandparent(alice, X).
```

requires two inference steps:

```text
grandparent(alice, X)
        ↓
parent(alice, Y), parent(Y, X)
        ↓
parent(bob, X)
        ↓
X = charlie
```

and therefore produces:

```text
X = charlie.
```

A query for an unsupported fact fails:

```text
?- parent(charlie, X).
false.
```

---

## Complexity

The computational behaviour of backward chaining is closely related to the size of the resulting search tree.

Let:

* $b$ be the number of applicable rules at a typical goal,
* $d$ be the maximum depth of a derivation.

In the worst case, depth-first search may explore

$$
O(b^d)
$$

branches before finding a solution or establishing failure.

Unlike breadth-first search, depth-first inference requires memory proportional primarily to the current derivation depth rather than the entire search frontier. Ignoring the size of substitutions and terms, the recursive search therefore requires approximately

$$
O(d)
$$

search-stack space.

However, substitutions and the logical terms generated along a branch also consume memory, and repeated rule applications can create increasingly large terms.

The practical performance of Prolog-style inference therefore depends heavily on:

* rule ordering,
* goal ordering,
* branching factor,
* recursion structure,
* depth of derivations,
* and the effectiveness of unification.

A poor ordering can cause the solver to explore a large or even infinite branch before reaching a successful alternative.

---

## Limitations

This project intentionally implements only a small subset of Prolog. It currently does not support:

* Negation as failure
* Cut (`!`)
* Arithmetic predicates
* Lists and list notation (`[H|T]`)
* Built-in predicates
* The full Prolog operator system
* Modules
* Constraint logic programming
* Tabling or memoization
* Search heuristics or clause indexing

The purpose is to expose the fundamental inference mechanisms rather than reproduce the complete Prolog language.

---

## Running the Interpreter

Run the interpreter with a Prolog knowledge base:

```bash
python main.py knowledge.pl
```

The knowledge base is loaded and an interactive REPL is started.

A query can then be entered in Prolog syntax:

```text
?- parent(alice, X).
X = bob ; X = diana.
```

The interpreter can also be started without a knowledge-base file:

```bash
python main.py
```

---

## Concepts Demonstrated

This project provides an implementation-level demonstration of:

* First-order logic
* Horn clauses
* Terms and predicates
* Substitutions
* Unification
* Most General Unifiers
* Occurs checking
* Standardization apart
* Backward chaining
* SLD-style resolution
* Depth-first search
* Backtracking
* Knowledge representation
* Logic-programming query evaluation

---

## Reference

Russell, S., & Norvig, P. (2010). *Artificial Intelligence: A Modern Approach* (3rd ed.). Prentice Hall. Chapter 9, *Inference in First-Order Logic*.
