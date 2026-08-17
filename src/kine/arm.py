from math import atan2, pi

from pydantic import BaseModel

from kine.build_nlp import build_forward_nlp, build_inverse_nlp
from kine.solve import RETRYABLE_REASONS, SolverResults, solve_with_ipopt
from kine.types import JointAngles, TipPosition


class TwoJointArm(BaseModel):
    l1: float
    l2: float
    angles: JointAngles = JointAngles(theta1=0.0, theta2=0.0)
    target: TipPosition = TipPosition(x=2.0, y=0.0)

    def tip_position(self, angles: JointAngles) -> SolverResults:
        nlp = build_forward_nlp(self.l1, self.l2, angles.theta1, angles.theta2)
        return solve_with_ipopt(nlp, x0=[0.0, 0.0])

    def set_target(self, position: TipPosition) -> SolverResults:
        self.target = position
        nlp = build_inverse_nlp(self.l1, self.l2, position.x, position.y)
        heading = atan2(position.y, position.x)
        guesses = [
            [self.angles.theta1, self.angles.theta2],
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
