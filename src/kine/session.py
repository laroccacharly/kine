from time import monotonic

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig
from kine.render import RenderConfig
from kine.solve import SolverResults, solve_inverse
from kine.trajectory import Trajectory
from kine.types import JointAngles, TipPosition


class ArmSession:
    def __init__(
        self,
        arm: TwoJointArm,
        motion_config: JointMotionConfig,
        render_config: RenderConfig,
    ) -> None:
        self.motion_config = motion_config
        self.render_config = render_config
        self.target = TipPosition(x=2.0, y=0.0)
        self.origin_s = monotonic()
        result = solve_inverse(arm, self.target)
        if result.success and result.solution is not None:
            self.goal = JointAngles(theta1=result.solution[0], theta2=result.solution[1])
            arm = arm.model_copy(update={"angles": self.goal})
        else:
            self.goal = arm.angles
        self.trajectory = Trajectory.hold(arm)

    def time_s(self) -> float:
        return monotonic() - self.origin_s

    def current_arm(self) -> TwoJointArm:
        return self.trajectory.get_arm_at(self.time_s())

    def set_motion_config(self, config: JointMotionConfig) -> None:
        start = self.current_arm()
        self.motion_config = config
        self.trajectory = Trajectory.plan(start=start, goal=self.goal, config=config)

    def set_target(self, target: TipPosition) -> SolverResults:
        self.target = target
        start = self.current_arm()
        result = solve_inverse(start, target)
        if result.success and result.solution is not None:
            self.goal = JointAngles(theta1=result.solution[0], theta2=result.solution[1])
            self.trajectory = Trajectory.plan(
                start=start,
                goal=self.goal,
                config=self.motion_config,
            )
        return result
