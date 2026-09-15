# Micro-Prolog: Unification and Backward-Chaining Inference

This project implements a small Prolog interpreter in Python grounded in the logic-programming concepts of Chapter 9 of *Artificial Intelligence: A Modern Approach* (Russell & Norvig, 2010). The implementation covers the core mechanisms underlying first-order logic inference: term representation, substitution, unification with occurs check, standardisation apart, and backward chaining with depth-first backtracking. The objective is a transparent realisation of these mechanisms rather than a complete Prolog system; the interpreter supports Prolog-style facts and Horn clauses, a knowledge-base query interface, and an interactive REPL.

Logic programming rests on Robert Kowalski's equation, *Algorithm = Logic + Control*: knowledge is expressed declaratively as logical sentences, and computation proceeds by running an inference procedure over that knowledge. Prolog is the most widely used realisation of this paradigm, employed in rapid prototyping, compiler construction, and natural language parsing (Russell & Norvig, 2010). This project exposes the inference machinery underlying Prolog at the implementation level.

---

## Project Architecture

| Module | Responsibility |
| :--- | :--- |
| `ast.py` | Representation of variables, atoms, compound terms, and Horn clauses |
| `unify.py` | Substitution application, occurs check, and unification |
| `kb.py` | Knowledge-base storage and standardisation apart |
| `solver.py` | Backward-chaining inference and depth-first backtracking |
| `parser.py` | Tokenisation and parsing of Prolog-style syntax |
| `main.py` | Knowledge-base loading and interactive REPL |

---

## Theoretical Background

### First-Order Logic and Horn Clauses

The interpreter operates on a restricted fragment of first-order logic consisting of **Horn clauses** — clauses containing at most one positive literal. In Prolog notation, a Horn clause is written

$$H \mathbin{:-} B_1, B_2, \ldots, B_n,$$

where $H$ is the **head** and $B_1, \ldots, B_n$ form the **body**, representing the logical implication $B_1 \land \cdots \land B_n \Rightarrow H$. A **fact** is a Horn clause with an empty body. The knowledge base is a collection of such clauses from which the interpreter attempts to establish queries via inference.

Prolog uses **database semantics** rather than full first-order semantics (Russell & Norvig, 2010). The **unique names assumption** treats every constant and ground term as referring to a distinct object; the **closed world assumption** treats any sentence not entailed by the knowledge base as false. These assumptions make Prolog more efficient and concise than full FOL reasoning, at the cost of expressiveness.

---

### Terms

First-order terms are represented using three types. **Variables** denote unknown values; **atoms** denote constants; **compound terms** consist of a functor applied to zero or more arguments, written $f(t_1, \ldots, t_n)$. A compound term is structurally determined by both its functor and its argument list, so $parent(alice, bob) \neq parent(alice, charlie)$. This recursive term structure is what allows unification to operate over arbitrary logical expressions.

---

### Substitution

A **substitution** $\theta$ is a finite mapping from variables to terms. Applying $\theta$ to a term replaces each variable with its bound value, resolving chains of variable bindings recursively. For example, the substitution $\theta = \{X \mapsto Y,\; Y \mapsto bob\}$ applied to $X$ yields $bob$ after recursive resolution. The implementation follows this recursive application when constructing and composing substitutions.

---

### Unification

**Unification** is the process of finding a substitution that makes two terms syntactically identical; the result is called a **unifier**. The *Unify* algorithm (Russell & Norvig, 2010) takes two expressions and a substitution built up so far, and proceeds by structural decomposition: two compound terms unify only when their functors are identical, their argument lists have the same length, and every corresponding pair of arguments unifies recursively. If the functors differ, unification fails immediately.

Among all unifiers for a pair of expressions, the interpreter seeks a **Most General Unifier (MGU)** — the substitution that imposes the fewest constraints, leaving variables as unconstrained as possible. The MGU is essential to logic programming because it preserves maximum generality at each inference step, avoiding unnecessary commitments to specific values.

**Occurs check.** When unifying a variable $X$ with a compound term $t$, a well-formed unifier requires that $X$ does not appear within $t$; otherwise, binding $X \mapsto t$ would produce a circular substitution that expands indefinitely under recursive application. The occurs check rejects such unifications. Russell & Norvig (2010) note that the occurs check makes unification quadratic in the size of the expressions; some Prolog systems omit it for efficiency, at the cost of potential unsound inferences. This implementation retains the occurs check.

---

### Standardisation Apart

Rules in the knowledge base are reused across many inference steps. Each application of a rule must use a fresh copy of its variables, independent of all previous applications, to prevent bindings established in one branch of the search from propagating incorrectly into another. This renaming process is called **standardisation apart**: before a rule is considered for unification, its variables are renamed using a globally maintained counter to generate unique identifiers. Without it, separate invocations of the same rule would share variable names and produce incorrect inference.

---

### Backward Chaining

The interpreter answers queries via **backward chaining**: rather than deriving all consequences of the knowledge base in advance, it starts from the desired goal and asks what facts or rule bodies would be sufficient to establish it. For a goal $G$ and a rule $H \mathbin{:-} B_1, \ldots, B_k$ whose head unifies with $G$ under substitution $\theta$, the original goal is replaced by the instantiated body $B_1\theta, \ldots, B_k\theta$, and the solver recurses. The base case occurs when the goal list is empty, at which point the accumulated substitution constitutes a solution.

This corresponds to **SLD-resolution** (Selective Linear Definite clause resolution) over the Horn-clause knowledge base. Generalized Modus Ponens — the lifted inference rule underlying backward chaining — is sound: every derivation it produces is a logical consequence of the knowledge base (Russell & Norvig, 2010).

---

### Depth-First Search and Backtracking

When multiple rules or facts can unify with a goal, the interpreter explores them via **depth-first search**, trying each candidate in the order it appears in the knowledge base. Upon finding a successful branch, the solver returns its substitution; when the user requests an additional solution, the interpreter backtracks to the most recent unresolved choice point and continues. If a branch fails entirely, the solver backtracks and tries the next candidate.

The ordering of clauses in the knowledge base therefore has a significant effect on search behaviour. A poorly ordered recursive rule can produce an infinite search path before a finite solution is found. For example, placing a recursive clause before a base case in a rule such as

```prolog
path(X, Z) :- path(X, Y), link(Y, Z).
path(X, Z) :- link(X, Z).
```

causes the interpreter to follow an infinite left-recursive branch, never reaching the base case — even when a finite proof exists. Prolog's depth-first strategy makes it incomplete in this sense: it may fail to find proofs that exist, depending on rule ordering and goal structure (Russell & Norvig, 2010). Reordering the clauses to place the base case first recovers termination for this class of problem.

---

### Redundant Inference and Memoisation

Depth-first backward chaining can perform substantial redundant computation by re-deriving the same subgoals across different branches of the search tree. For graph reachability problems, for instance, Prolog may perform exponentially many inferences where forward chaining would require at most $n^2$ — one for each pair of nodes (Russell & Norvig, 2010). This is analogous to the repeated-state problem in uninformed search.

The standard remedy is **memoisation**: caching solutions to subgoals as they are found and reusing them when the same subgoal recurs, rather than repeating the derivation. This approach is taken by tabled logic programming systems, which combine the goal-directedness of backward chaining with the dynamic-programming efficiency of forward chaining. This interpreter does not implement tabling, and is therefore subject to redundant inference on recursive knowledge bases.

---

### Soundness and Completeness

**Soundness.** Every successful derivation corresponds to a logical consequence of the Horn-clause knowledge base, since each inference step is an application of Generalized Modus Ponens, which is sound.

**Completeness.** Given a finite search space and terminating derivations, depth-first backward chaining finds every logically derivable solution. In practice, unrestricted recursive rules can produce infinite branches under depth-first evaluation, so termination is not guaranteed and logical completeness does not imply that every query terminates.

---

## Limitations

This project implements a minimal subset of Prolog sufficient to demonstrate the core inference mechanisms. The following features are intentionally omitted:

- Negation as failure
- Cut (`!`)
- Arithmetic predicates and built-in functions
- List notation (`[H|T]`)
- Modules and operator declarations
- Tabling and memoisation
- Clause indexing and the Warren Abstract Machine

---

## Example

A simple family knowledge base:

```prolog
parent(alice, bob).
parent(bob, charlie).
parent(alice, diana).

grandparent(X, Z) :- parent(X, Y), parent(Y, Z).
```

Query:

```prolog
?- grandparent(alice, X).
X = charlie.
```

The derivation proceeds as follows: `grandparent(alice, X)` unifies with the rule head under $\{A \mapsto alice,\; C \mapsto X\}$, replacing the goal with `parent(alice, Y), parent(Y, X)`. The first conjunct unifies with `parent(alice, bob)`, binding $Y \mapsto bob$, leaving `parent(bob, X)`. This unifies with `parent(bob, charlie)`, binding $X \mapsto charlie$ and closing the proof.

---

## Reproduction

```bash
python main.py family.pl
```

---

## References

Russell, S., & Norvig, P. (2010). *Artificial Intelligence: A Modern Approach* (3rd ed.). Prentice Hall. Chapter 9, *Inference in First-Order Logic*.
