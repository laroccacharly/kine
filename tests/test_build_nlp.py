import casadi as ca

from kine.build_nlp import NlpProblem, build_forward_nlp, build_inverse_nlp


def test_forward_problem_exposes_its_layers() -> None:
    problem = build_forward_nlp(1.0, 1.0, 0.0, 0.0)

    assert isinstance(problem, NlpProblem)
    assert [problem.variables[i].name() for i in range(2)] == ["x", "y"]
    assert problem.objective.is_zero()
    assert problem.constraints.shape == (2, 1)


def test_inverse_problem_exposes_its_layers() -> None:
    problem = build_inverse_nlp(1.0, 1.0, 2.0, 0.0)

    assert isinstance(problem, NlpProblem)
    assert [problem.variables[i].name() for i in range(2)] == ["theta1", "theta2"]
    assert problem.objective.is_zero()
    assert problem.constraints.shape == (2, 1)


def test_problem_translates_to_casadi_nlp_keys() -> None:
    variable = ca.SX.sym("value")
    problem = NlpProblem(
        variables=variable,
        objective=variable**2,
        constraints=variable - 1,
    )

    assert problem.to_casadi() == {
        "x": problem.variables,
        "f": problem.objective,
        "g": problem.constraints,
    }
