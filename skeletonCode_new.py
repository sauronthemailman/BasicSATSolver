def load_dimacs(file_name):
    # file_name will be of the form "problem_name.txt"
    ...
    clauses = []

    with open(file_name, "r") as f:
        for line in f:
            line = line.strip()  # remove leading/trailing spaces
            if not line:
                continue  # skip empty lines
            if line[0] == "p":
                continue  # skip first line
            clause = list(map(int, line.split()))  # convert literals to integers
            clause.pop()  # removes 0 at the end
            clauses.append(clause)  # update cluase

        return clauses


def simple_sat_solver(clause_set):

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

    # extract unique variables from the clause set
    variables = sorted(get_variables(clause_set))
    num_vars = len(variables)

    # iterate over all possible assignments
    for i in range(1 << num_vars):  # 2^num_vars possible assignments
        assignment = set()

        # construct truth assignment for the current iteration
        for j in range(num_vars):
            if i & (1 << j):  # If the j-th bit of i is set
                assignment.add(variables[j])  # Assign variable to True
            else:
                assignment.add(
                    variables[j] * -1
                )  # Assign variable to Not True (Not False)

        # Check if this assignment satisfies all clauses
        satisfied = True
        for clause in clause_set:
            if not evaluate_clause(clause, assignment):
                satisfied = False
                break

        if satisfied:
            return list(assignment)  # Return satisfying assignment as a list

    return False  # No satisfying assignment found

print(simple_sat_solve([[1], [1, -1], [-1, -2]]))
def branching_sat_solve(clause_set, partial_assignment): ...


def unit_propagate(clause_set): ...


def dpll_sat_solve(clause_set, partial_assignment): ...


def test():
    print("Testing load_dimacs")
    try:
        dimacs = load_dimacs("sat.txt")
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
