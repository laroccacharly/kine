from bisect import bisect_right
from math import remainder, tau

from pydantic import BaseModel, Field

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig, advance_arm, arm_has_settled
from kine.types import JointAngles

PLAN_DT_S = 1 / 60
PLAN_MAX_DURATION_S = 30.0


class Trajectory(BaseModel):
    samples: list[TwoJointArm] = Field(min_length=1)

    @classmethod
    def hold(cls, arm: TwoJointArm) -> "Trajectory":
        return cls(samples=[arm])

    @classmethod
    def plan(
        cls,
        start: TwoJointArm,
        goal: JointAngles,
        config: JointMotionConfig,
        dt_s: float = PLAN_DT_S,
        max_duration_s: float = PLAN_MAX_DURATION_S,
    ) -> "Trajectory":
        samples = [start]
        arm = start
        while arm.t_s - start.t_s < max_duration_s and not arm_has_settled(
            arm, goal, config
        ):
            arm = advance_arm(arm, goal, dt_s, config)
            samples.append(arm)
        return cls(samples=samples)

    def get_arm_at(self, t_s: float) -> TwoJointArm:
        if t_s <= self.samples[0].t_s:
            return self.samples[0].model_copy(update={"t_s": t_s})
        if t_s >= self.samples[-1].t_s:
            return self.samples[-1].model_copy(update={"t_s": t_s})
        times = [sample.t_s for sample in self.samples]
        after = bisect_right(times, t_s)
        left = self.samples[after - 1]
        right = self.samples[after]
        span_s = right.t_s - left.t_s
        blend = 0.0 if span_s <= 0 else (t_s - left.t_s) / span_s
        return interpolate_arm(left, right, t_s, blend)


def interpolate_angle_rad(start_rad: float, end_rad: float, blend: float) -> float:
    return start_rad + remainder(end_rad - start_rad, tau) * blend


def interpolate_arm(start: TwoJointArm, end: TwoJointArm, t_s: float, blend: float) -> TwoJointArm:
    return start.model_copy(
        update={
            "t_s": t_s,
            "angles": JointAngles(
                theta1=interpolate_angle_rad(start.angles.theta1, end.angles.theta1, blend),
                theta2=interpolate_angle_rad(start.angles.theta2, end.angles.theta2, blend),
            ),
            "speed1_rad_s": start.speed1_rad_s + (end.speed1_rad_s - start.speed1_rad_s) * blend,
            "speed2_rad_s": start.speed2_rad_s + (end.speed2_rad_s - start.speed2_rad_s) * blend,
        }
    )
