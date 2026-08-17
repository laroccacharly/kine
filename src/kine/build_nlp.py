import casadi as ca


def tip_coordinates(
    l1: float, l2: float, theta1: ca.SX | float, theta2: ca.SX | float
) -> tuple[ca.SX | float, ca.SX | float]:
    x = l1 * ca.cos(theta1) + l2 * ca.cos(theta1 + theta2)
    y = l1 * ca.sin(theta1) + l2 * ca.sin(theta1 + theta2)
    return x, y


def build_forward_nlp(l1: float, l2: float, theta1: float, theta2: float) -> dict:
    x = ca.SX.sym("x")
    y = ca.SX.sym("y")
    expected_x, expected_y = tip_coordinates(l1, l2, theta1, theta2)
    return {
        "x": ca.vertcat(x, y),
        "f": 0,
        "g": ca.vertcat(x - expected_x, y - expected_y),
    }


def build_inverse_nlp(l1: float, l2: float, x: float, y: float) -> dict:
    theta1 = ca.SX.sym("theta1")
    theta2 = ca.SX.sym("theta2")
    tip_x, tip_y = tip_coordinates(l1, l2, theta1, theta2)
    return {
        "x": ca.vertcat(theta1, theta2),
        "f": 0,
        "g": ca.vertcat(tip_x - x, tip_y - y),
    }
