from math import copysign, remainder, tau

from pydantic import BaseModel, Field

from kine.types import JointAngles


class JointMotionConfig(BaseModel):
    max_speed_rad_s: float = Field(default=2.0, gt=0)
    acceleration_rad_s2: float = Field(default=6.0, gt=0)
    settle_rad: float = Field(default=1e-4, gt=0)


class JointState(BaseModel):
    angle_rad: float
    speed_rad_s: float = 0.0


class JointMotion(BaseModel):
    config: JointMotionConfig
    goal: JointAngles
    joint1: JointState
    joint2: JointState

    @classmethod
    def at_rest(cls, angles: JointAngles, config: JointMotionConfig) -> "JointMotion":
        return cls(
            config=config,
            goal=angles,
            joint1=JointState(angle_rad=angles.theta1),
            joint2=JointState(angle_rad=angles.theta2),
        )

    @property
    def angles(self) -> JointAngles:
        return JointAngles(theta1=self.joint1.angle_rad, theta2=self.joint2.angle_rad)

    def set_goal(self, goal: JointAngles) -> None:
        self.goal = goal

    def step(self, dt_s: float) -> JointAngles:
        self.joint1 = step_joint(self.joint1, self.goal.theta1, dt_s, self.config)
        self.joint2 = step_joint(self.joint2, self.goal.theta2, dt_s, self.config)
        return self.angles


def angle_error_rad(current_rad: float, target_rad: float) -> float:
    return remainder(target_rad - current_rad, tau)


def commanded_acceleration_rad_s2(
    error_rad: float,
    speed_rad_s: float,
    config: JointMotionConfig,
) -> float:
    accel = config.acceleration_rad_s2
    if abs(error_rad) < config.settle_rad:
        if abs(speed_rad_s) < config.settle_rad:
            return 0.0
        return -copysign(accel, speed_rad_s)

    moving_toward_target = speed_rad_s * error_rad > 0
    stop_distance_rad = speed_rad_s * speed_rad_s / (2 * accel)
    if moving_toward_target and stop_distance_rad >= abs(error_rad):
        return -copysign(accel, speed_rad_s)
    return copysign(accel, error_rad)


def step_joint(
    state: JointState,
    target_rad: float,
    dt_s: float,
    config: JointMotionConfig,
) -> JointState:
    if dt_s <= 0:
        return state

    error_rad = angle_error_rad(state.angle_rad, target_rad)
    if abs(error_rad) < config.settle_rad and abs(state.speed_rad_s) < config.settle_rad:
        return JointState(angle_rad=target_rad, speed_rad_s=0.0)

    accel_rad_s2 = commanded_acceleration_rad_s2(error_rad, state.speed_rad_s, config)
    new_speed_rad_s = state.speed_rad_s + accel_rad_s2 * dt_s
    braking = accel_rad_s2 * state.speed_rad_s < 0
    if braking and new_speed_rad_s * state.speed_rad_s <= 0:
        new_speed_rad_s = 0.0

    max_speed = config.max_speed_rad_s
    new_speed_rad_s = min(max(new_speed_rad_s, -max_speed), max_speed)
    new_angle_rad = state.angle_rad + new_speed_rad_s * dt_s
    new_error_rad = angle_error_rad(new_angle_rad, target_rad)
    if error_rad * new_error_rad <= 0:
        return JointState(angle_rad=target_rad, speed_rad_s=0.0)
    return JointState(angle_rad=new_angle_rad, speed_rad_s=new_speed_rad_s)
