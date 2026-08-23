from math import atan2, pi
from time import perf_counter

import casadi as ca
from pydantic import BaseModel

from kine.arm import TwoJointArm
from kine.build_nlp import build_forward_nlp, build_inverse_nlp
from kine.types import JointAngles, TipPosition

IPOPT_OPTIONS = {
    "ipopt.print_level": 0,
    "ipopt.sb": "yes",
    "print_time": False,
    "verbose": False,
}

RETRYABLE_REASONS = {
    "Diverging_Iterates",
    "Infeasible_Problem_Detected",
    "Restoration_Failure",
}


class SolverResults(BaseModel):
    success: bool
    solution: list[float] | None
    reason: str
    runtime: float


def solve_with_ipopt(nlp: dict, x0: list[float]) -> SolverResults:
    started = perf_counter()
    solver = ca.nlpsol("kinematics", "ipopt", nlp, IPOPT_OPTIONS)
    result = solver(x0=x0, lbg=[0, 0], ubg=[0, 0])
    runtime = perf_counter() - started
    stats = solver.stats()
    if not stats["success"]:
        return SolverResults(
            success=False,
            solution=None,
            reason=str(stats.get("return_status", "solve failed")),
            runtime=runtime,
        )
    values = result["x"]
    return SolverResults(
        success=True,
        solution=[float(values[0]), float(values[1])],
        reason=str(stats.get("return_status", "Solve_Succeeded")),
        runtime=runtime,
    )


def solve_forward(arm: TwoJointArm, angles: JointAngles) -> SolverResults:
    nlp = build_forward_nlp(arm.l1, arm.l2, angles.theta1, angles.theta2)
    return solve_with_ipopt(nlp, x0=[0.0, 0.0])


def solve_inverse(arm: TwoJointArm, target: TipPosition) -> SolverResults:
    nlp = build_inverse_nlp(arm.l1, arm.l2, target.x, target.y)
    heading = atan2(target.y, target.x)
    guesses = [
        [arm.angles.theta1, arm.angles.theta2],
        [heading, 0.0],
        [heading, pi / 2],
        [heading, -pi / 2],
        [heading + pi, 0.0],
    ]
    runtime = 0.0
    last = SolverResults(success=False, solution=None, reason="solve failed", runtime=0.0)
    for seed in guesses:
        result = solve_with_ipopt(nlp, x0=seed)
        runtime += result.runtime
        last = SolverResults(
            success=result.success,
            solution=result.solution,
            reason=result.reason,
            runtime=runtime,
        )
        if result.success:
            return last
        if result.reason not in RETRYABLE_REASONS:
            return last
    return last
