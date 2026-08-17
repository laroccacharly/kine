from math import isclose, remainder, tau

from pydantic import BaseModel


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
