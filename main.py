import sys
from kb import KnowledgeBase
from parser import parse_line, PrologParser
from solver import query


def load_file(filename, kb):
    """Reads a .pl file line-by-line and loads rules/facts into the KB."""
    try:
        with open(filename, 'r') as f:
            count = 0
            for line in f:
                # Strip spaces and carriage returns
                line = line.strip()
                if not line or line.startswith('%'):
                    continue
                rule = parse_line(line)
                if rule:
                    kb.tell(rule)
                    count += 1
            print(f"[*] Successfully loaded {count} rules/facts from '{filename}'.")
    except FileNotFoundError:
        print(f"[!] Error: File '{filename}' not found.")


def run_repl(kb):
    """Launches the interactive Prolog REPL loop."""
    print("\n==========================================")
    print(" Micro-Prolog Engine (Chapter 9 AIMA)")
    print(" Type a query (e.g. 'parent(alice, bob).')")
    print(" Press Ctrl+C or type 'quit' to exit.")
    print("==========================================\n")

    while True:
        try:
            raw_input = input("?- ").strip()
            if not raw_input:
                continue
            if raw_input in ["exit", "quit"]:
                break

            # Ensure trailing period
            if not raw_input.endswith('.'):
                raw_input += '.'

            # Parse input as a Rule statement
            parsed_statement = parse_line(raw_input)
            if not parsed_statement:
                continue

            # A query's target goal is the head of the parsed statement
            query_goal = parsed_statement.head

            # Run solver query
            solutions = list(query(query_goal, kb))

            if not solutions:
                print("false.")
            else:
                for idx, sol in enumerate(solutions):
                    # Fact query succeeded with no variable bindings
                    if sol == {}:
                        print("true.")
                        break

                    # Query with variables (e.g., Child = bob)
                    bindings = [f"{var.name} = {val}" for var, val in sol.items()]
                    output = ", ".join(bindings)

                    if idx < len(solutions) - 1:
                        user_choice = input(f"{output} ; ").strip()
                        if user_choice != ';':
                            break
                    else:
                        print(f"{output}.")

        except KeyboardInterrupt:
            print("\nExiting Micro-Prolog. Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    kb = KnowledgeBase()

    if len(sys.argv) > 1:
        load_file(sys.argv[1], kb)

    run_repl(kb)