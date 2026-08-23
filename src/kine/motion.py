from math import copysign, remainder, tau

from pydantic import BaseModel, Field

from kine.arm import TwoJointArm
from kine.types import JointAngles


class JointMotionConfig(BaseModel):
    max_speed_rad_s: float = Field(default=2.0, gt=0)
    acceleration_rad_s2: float = Field(default=6.0, gt=0)
    settle_rad: float = Field(default=1e-4, gt=0)


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


def joint_settled(
    angle_rad: float,
    speed_rad_s: float,
    target_rad: float,
    config: JointMotionConfig,
) -> bool:
    error_rad = angle_error_rad(angle_rad, target_rad)
    return abs(error_rad) < config.settle_rad and abs(speed_rad_s) < config.settle_rad


def step_joint(
    angle_rad: float,
    speed_rad_s: float,
    target_rad: float,
    dt_s: float,
    config: JointMotionConfig,
) -> tuple[float, float]:
    if dt_s <= 0:
        return angle_rad, speed_rad_s

    error_rad = angle_error_rad(angle_rad, target_rad)
    if joint_settled(angle_rad, speed_rad_s, target_rad, config):
        return target_rad, 0.0

    accel_rad_s2 = commanded_acceleration_rad_s2(error_rad, speed_rad_s, config)
    new_speed_rad_s = speed_rad_s + accel_rad_s2 * dt_s
    braking = accel_rad_s2 * speed_rad_s < 0
    if braking and new_speed_rad_s * speed_rad_s <= 0:
        new_speed_rad_s = 0.0

    max_speed = config.max_speed_rad_s
    new_speed_rad_s = min(max(new_speed_rad_s, -max_speed), max_speed)
    new_angle_rad = angle_rad + new_speed_rad_s * dt_s
    new_error_rad = angle_error_rad(new_angle_rad, target_rad)
    if error_rad * new_error_rad <= 0:
        return target_rad, 0.0
    return new_angle_rad, new_speed_rad_s


def arm_settled(arm: TwoJointArm, goal: JointAngles, config: JointMotionConfig) -> bool:
    return joint_settled(
        arm.angles.theta1, arm.speed1_rad_s, goal.theta1, config
    ) and joint_settled(arm.angles.theta2, arm.speed2_rad_s, goal.theta2, config)


def step_arm(
    arm: TwoJointArm,
    goal: JointAngles,
    dt_s: float,
    config: JointMotionConfig,
) -> TwoJointArm:
    theta1, speed1_rad_s = step_joint(
        arm.angles.theta1, arm.speed1_rad_s, goal.theta1, dt_s, config
    )
    theta2, speed2_rad_s = step_joint(
        arm.angles.theta2, arm.speed2_rad_s, goal.theta2, dt_s, config
    )
    return arm.model_copy(
        update={
            "t_s": arm.t_s + dt_s,
            "angles": JointAngles(theta1=theta1, theta2=theta2),
            "speed1_rad_s": speed1_rad_s,
            "speed2_rad_s": speed2_rad_s,
        }
    )
