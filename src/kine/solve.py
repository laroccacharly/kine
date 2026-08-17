import casadi as ca

IPOPT_OPTIONS = {
    "ipopt.print_level": 0,
    "ipopt.sb": "yes",
    "print_time": False,
    "verbose": False,
}


def solve_with_ipopt(nlp: dict, x0: list[float]) -> list[float]:
    solver = ca.nlpsol("kinematics", "ipopt", nlp, IPOPT_OPTIONS)
    result = solver(x0=x0, lbg=[0, 0], ubg=[0, 0])
    if not solver.stats()["success"]:
        raise RuntimeError("Ipopt failed to solve the kinematics problem")
    values = result["x"]
    return [float(values[0]), float(values[1])]
