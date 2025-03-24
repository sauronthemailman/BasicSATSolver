import time
def load_dimacs(file_name):
    clauses = []

    with open(file_name, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line[0] == "p":  
                continue
            clause = list(map(int, line.split()))
            clause.pop()  
            clauses.append(clause)

    return clauses


def simple_sat_solve(clause_set):

    def evaluate_clause(clause, assignment):

        for literal in clause:
            if literal in assignment:
                return True
        return False

    def get_variables(clause_set):

        variables = set()
        for clause in clause_set:
            for literal in clause:
                variables.add(abs(literal))
        return variables

    # extract unique variables
    variables = sorted(get_variables(clause_set))
    num_vars = len(variables)

    # iterate over all possible assignments
    for i in range(1 << num_vars):  # 2^num_vars possible assignments
        assignment = set()

        # construct truth assignment
        for j in range(num_vars):
            if i & (1 << j):
                assignment.add(variables[j])
            else:
                assignment.add(variables[j] * -1)
        satisfied = True
        for clause in clause_set:
            if not evaluate_clause(clause, assignment):
                satisfied = False
                break

        if satisfied:
            return list(assignment)

    return False


def branching_sat_solve(clause_set, partial_assignment):

    def is_satisfied(clause, assignment):
        for literal in clause:
            if literal in assignment:
                return True
        return False

    def is_conflicting(clause, assignment):
        for literal in clause:
            if literal not in assignment and -literal not in assignment:
                return False
        return True

    all_satisfied = True
    for clause in clause_set:
        if not is_satisfied(clause, partial_assignment):
            all_satisfied = False
            break

    if all_satisfied:
        return partial_assignment

    for clause in clause_set:
        if is_conflicting(clause, partial_assignment):
            return False

    all_literals = set()
    for clause in clause_set:
        for literal in clause:
            all_literals.add(abs(literal))

    assigned_literals = set()
    for lit in partial_assignment:
        assigned_literals.add(abs(lit))

    unassigned_literals = all_literals - assigned_literals

    if not unassigned_literals:
        return False

    unassigned = next(iter(unassigned_literals))

    new_assignment = partial_assignment + [unassigned]
    result = branching_sat_solve(clause_set, new_assignment)
    if result:
        return result

    new_assignment = partial_assignment + [-unassigned]
    return branching_sat_solve(clause_set, new_assignment)


def unit_propagate(clause_set):
    simplified_clauses = [set(clause) for clause in clause_set]
    unit_literals = {clause.pop() for clause in simplified_clauses if len(clause) == 1}

    while unit_literals:
        new_simplified_clauses = []
        new_unit_literals = set()

        for clause in simplified_clauses:
            if unit_literals & clause:
                continue
            new_clause = clause - {
                -lit for lit in unit_literals
            }  # Remove negated unit literals
            if not new_clause:  # Empty clause indicates a conflict
                return []  # Return an empty list to signify contradiction
            if len(new_clause) == 1:
                new_unit_literals.add(next(iter(new_clause)))
            new_simplified_clauses.append(new_clause)

        simplified_clauses = new_simplified_clauses
        unit_literals = new_unit_literals

    return simplified_clauses


def dpll_sat_solve(clause_set, partial_assignment):

    def is_satisfied(clause, assignment):

        for literal in clause:
            if literal in assignment:
                return True
            elif -literal in assignment:
                continue
        return False

    def is_unsatisfied(clause, assignment):

        for literal in clause:
            if literal in assignment:
                return False
            elif -literal in assignment:
                continue
        return True

    def all_clauses_satisfied(clause_set, assignment):

        for clause in clause_set:
            if not is_satisfied(clause, assignment):
                return False
        return True

    def any_clause_unsatisfied(clause_set, assignment):

        for clause in clause_set:
            if is_unsatisfied(clause, assignment):
                return True
        return False

    def unit_propagate(clause_set, assignment):

        def find_unit_clauses(clause_set, assignment):
            unit_clauses = []
            for clause in clause_set:
                if len(clause) == 1:
                    unit_clauses.append(clause[0])
                else:
                    unit_clause_candidate = None
                    all_false = True
                    for literal in clause:
                        if literal in assignment:
                            all_false = False
                            break
                        elif -literal in assignment:
                            continue
                        else:
                            if unit_clause_candidate is None:
                                unit_clause_candidate = literal
                            else:
                                all_false = False
                                break
                    if all_false and unit_clause_candidate is not None:
                        unit_clauses.append(unit_clause_candidate)
            return unit_clauses

        def simplify_clause_set(clause_set, assignment):
            new_clause_set = []
            for clause in clause_set:
                simplified_clause = []
                satisfied = False
                for literal in clause:
                    if literal in assignment:
                        satisfied = True
                        break
                    elif -literal not in assignment:
                        simplified_clause.append(literal)
                if not satisfied:
                    if len(simplified_clause) > 0:
                        new_clause_set.append(simplified_clause)
                    elif len(simplified_clause) == 0:
                        return None
            return new_clause_set

        new_assignment = assignment[:]
        new_clause_set = clause_set[:]

        while True:
            unit_clauses = find_unit_clauses(new_clause_set, new_assignment)
            if not unit_clauses:
                break

            for unit_literal in unit_clauses:
                if -unit_literal in new_assignment:
                    return None, None
                new_assignment.append(unit_literal)

            simplified = simplify_clause_set(new_clause_set, new_assignment)
            if simplified is None:
                return None, None
            else:
                new_clause_set = simplified

        return new_clause_set, new_assignment

    simplified_clause_set, simplified_assignment = unit_propagate(
        clause_set, partial_assignment
    )

    if simplified_clause_set is None:
        return False

    if any_clause_unsatisfied(simplified_clause_set, simplified_assignment):
        return False

    if all_clauses_satisfied(simplified_clause_set, simplified_assignment):
        return simplified_assignment

    variables = set()
    for clause in simplified_clause_set:
        for literal in clause:
            variables.add(abs(literal))

    assigned_variables = set(abs(literal) for literal in simplified_assignment)
    unassigned_variables = variables - assigned_variables

    if not unassigned_variables:
        return False

    variable = unassigned_variables.pop()

    result_true = dpll_sat_solve(
        simplified_clause_set, simplified_assignment + [variable]
    )
    if result_true:
        return result_true

    result_false = dpll_sat_solve(
        simplified_clause_set, simplified_assignment + [-variable]
    )
    if result_false:
        return result_false

    return False


def test():
    print("Testing load_dimacs")
    try:
        dimacs = load_dimacs("8queens.txt")
        assert dimacs == [[1], [1, -1], [-1, -2]]
        print("Test passed")
    except:
        print("Failed to correctly load DIMACS file")

    print("Testing simple_sat_solve")
    try:
        sat1 = [[1], [1, -1], [-1, -2]]
        check = simple_sat_solve(sat1)
        assert check == [1, -2] or check == [-2, 1]
        print("Test (SAT) passed")
    except:
        print("simple_sat_solve did not work correctly a sat instance")

    try:
        unsat1 = [[1, -2], [-1, 2], [-1, -2], [1, 2]]
        check = simple_sat_solve(unsat1)
        assert not check
        print("Test (UNSAT) passed")
    except:
        print("simple_sat_solve did not work correctly an unsat instance")

    print("Testing branching_sat_solve")
    try:
        sat1 = [[1], [1, -1], [-1, -2]]
        check = branching_sat_solve(sat1, [])
        assert check == [1, -2] or check == [-2, 1]
        print("Test (SAT) passed")
    except:
        print("branching_sat_solve did not work correctly a sat instance")

    try:
        unsat1 = [[1, -2], [-1, 2], [-1, -2], [1, 2]]
        check = branching_sat_solve(unsat1, [])
        assert not check
        print("Test (UNSAT) passed")
    except:
        print("branching_sat_solve did not work correctly an unsat instance")

    print("Testing unit_propagate")
    try:
        clause_set = [[1], [-1, 2]]
        check = unit_propagate(clause_set)
        assert check == []
        print("Test passed")
    except:
        print("unit_propagate did not work correctly")

    print("Testing DPLL")  # Note, this requires load_dimacs to work correctly
    problem_names = ["sat.txt", "unsat.txt"]
    for problem in problem_names:
        try:
            clause_set = load_dimacs(problem)
            check = dpll_sat_solve(clause_set, [])
            if problem == problem_names[1]:
                assert not check
                print("Test (UNSAT) passed")
            else:
                assert check == [1, -2] or check == [-2, 1]
                print("Test (SAT) passed")
        except:
            print("Failed problem " + str(problem))
    print("Finished tests")


test()
time.time(test())
