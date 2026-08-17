from time import perf_counter

import casadi as ca
from pydantic import BaseModel

IPOPT_OPTIONS = {
    "ipopt.print_level": 0,
    "ipopt.sb": "yes",
    "print_time": False,
    "verbose": False,
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
