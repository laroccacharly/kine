from enum import StrEnum
from math import copysign, remainder, tau

from pydantic import BaseModel, Field

from kine.arm import TwoJointArm
from kine.types import JointAngles


class JointMotionConfig(BaseModel):
    max_speed_rad_s: float = Field(default=2.0, gt=0)
    acceleration_rad_s2: float = Field(default=6.0, gt=0)
    settle_rad: float = Field(default=1e-4, gt=0)


class JointMotionState(BaseModel):
    """The position and velocity of one rotating joint at an instant."""

    angle_rad: float
    speed_rad_s: float


class MotionPhase(StrEnum):
    ACCELERATE = "accelerate"
    BRAKE = "brake"
    SETTLED = "settled"


def shortest_angle_to_target_rad(current_rad: float, target_rad: float) -> float:
    """Signed shortest rotation from the current angle to the target angle."""
    return remainder(target_rad - current_rad, tau)


def stopping_distance_rad(speed_rad_s: float, acceleration_rad_s2: float) -> float:
    """Angular distance needed to stop under constant acceleration."""
    return speed_rad_s**2 / (2 * acceleration_rad_s2)


def motion_phase(
    state: JointMotionState,
    target_rad: float,
    config: JointMotionConfig,
) -> MotionPhase:
    """Choose whether the joint should speed up, slow down, or remain still."""
    angle_remaining_rad = shortest_angle_to_target_rad(state.angle_rad, target_rad)
    close_to_target = abs(angle_remaining_rad) < config.settle_rad
    nearly_stopped = abs(state.speed_rad_s) < config.settle_rad
    if close_to_target and nearly_stopped:
        return MotionPhase.SETTLED
    if close_to_target:
        return MotionPhase.BRAKE

    moving_toward_target = state.speed_rad_s * angle_remaining_rad > 0
    must_brake_now = stopping_distance_rad(
        state.speed_rad_s, config.acceleration_rad_s2
    ) >= abs(angle_remaining_rad)
    if moving_toward_target and must_brake_now:
        return MotionPhase.BRAKE
    return MotionPhase.ACCELERATE


def acceleration_for_phase_rad_s2(
    phase: MotionPhase,
    state: JointMotionState,
    target_rad: float,
    config: JointMotionConfig,
) -> float:
    if phase is MotionPhase.SETTLED:
        return 0.0
    if phase is MotionPhase.BRAKE:
        return -copysign(config.acceleration_rad_s2, state.speed_rad_s)

    angle_remaining_rad = shortest_angle_to_target_rad(state.angle_rad, target_rad)
    return copysign(config.acceleration_rad_s2, angle_remaining_rad)


def advance_joint(
    state: JointMotionState,
    target_rad: float,
    dt_s: float,
    config: JointMotionConfig,
) -> JointMotionState:
    """Advance one joint by one time step using semi-implicit Euler integration."""
    if dt_s <= 0:
        return state

    phase = motion_phase(state, target_rad, config)
    if phase is MotionPhase.SETTLED:
        return JointMotionState(angle_rad=target_rad, speed_rad_s=0.0)

    acceleration_rad_s2 = acceleration_for_phase_rad_s2(
        phase, state, target_rad, config
    )
    next_speed_rad_s = state.speed_rad_s + acceleration_rad_s2 * dt_s

    # Braking must not reverse the joint away from its target.
    if phase is MotionPhase.BRAKE and next_speed_rad_s * state.speed_rad_s <= 0:
        next_speed_rad_s = 0.0
    next_speed_rad_s = max(
        -config.max_speed_rad_s,
        min(next_speed_rad_s, config.max_speed_rad_s),
    )

    next_angle_rad = state.angle_rad + next_speed_rad_s * dt_s
    before_step_rad = shortest_angle_to_target_rad(state.angle_rad, target_rad)
    after_step_rad = shortest_angle_to_target_rad(next_angle_rad, target_rad)
    if before_step_rad * after_step_rad <= 0:
        return JointMotionState(angle_rad=target_rad, speed_rad_s=0.0)
    return JointMotionState(
        angle_rad=next_angle_rad,
        speed_rad_s=next_speed_rad_s,
    )


def arm_has_settled(
    arm: TwoJointArm,
    goal: JointAngles,
    config: JointMotionConfig,
) -> bool:
    joint1 = JointMotionState(
        angle_rad=arm.angles.theta1,
        speed_rad_s=arm.speed1_rad_s,
    )
    joint2 = JointMotionState(
        angle_rad=arm.angles.theta2,
        speed_rad_s=arm.speed2_rad_s,
    )
    return (
        motion_phase(joint1, goal.theta1, config) is MotionPhase.SETTLED
        and motion_phase(joint2, goal.theta2, config) is MotionPhase.SETTLED
    )


def advance_arm(
    arm: TwoJointArm,
    goal: JointAngles,
    dt_s: float,
    config: JointMotionConfig,
) -> TwoJointArm:
    """Advance both independent joint controllers by one time step."""
    joint1 = advance_joint(
        JointMotionState(
            angle_rad=arm.angles.theta1,
            speed_rad_s=arm.speed1_rad_s,
        ),
        goal.theta1,
        dt_s,
        config,
    )
    joint2 = advance_joint(
        JointMotionState(
            angle_rad=arm.angles.theta2,
            speed_rad_s=arm.speed2_rad_s,
        ),
        goal.theta2,
        dt_s,
        config,
    )
    return arm.model_copy(
        update={
            "t_s": arm.t_s + dt_s,
            "angles": JointAngles(
                theta1=joint1.angle_rad,
                theta2=joint2.angle_rad,
            ),
            "speed1_rad_s": joint1.speed_rad_s,
            "speed2_rad_s": joint2.speed_rad_s,
        }
    )
