from math import atan2, isclose, remainder, tau

from pydantic import BaseModel

from kine.build_nlp import build_forward_nlp, build_inverse_nlp
from kine.solve import solve_with_ipopt


def equivalent_angle(left: float, right: float) -> bool:
    return isclose(remainder(left - right, tau), 0.0, abs_tol=1e-5)


class JointAngles(BaseModel):
    theta1: float
    theta2: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JointAngles):
            return NotImplemented
        return equivalent_angle(self.theta1, other.theta1) and equivalent_angle(
            self.theta2, other.theta2
        )


class TipPosition(BaseModel):
    x: float
    y: float

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TipPosition):
            return NotImplemented
        return isclose(self.x, other.x, abs_tol=1e-5) and isclose(
            self.y, other.y, abs_tol=1e-5
        )


class TwoJointArm(BaseModel):
    l1: float
    l2: float

    def tip_position(self, angles: JointAngles) -> TipPosition:
        nlp = build_forward_nlp(self.l1, self.l2, angles.theta1, angles.theta2)
        solved_x, solved_y = solve_with_ipopt(nlp, x0=[0.0, 0.0])
        return TipPosition(x=solved_x, y=solved_y)

    def joint_angles(self, position: TipPosition) -> list[JointAngles]:
        nlp = build_inverse_nlp(self.l1, self.l2, position.x, position.y)
        guess = [atan2(position.y, position.x), 0.0]
        solved_theta1, solved_theta2 = solve_with_ipopt(nlp, x0=guess)
        return [JointAngles(theta1=solved_theta1, theta2=solved_theta2)]
