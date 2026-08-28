import pytest

from kine.motion import (
    JointMotionConfig,
    JointMotionState,
    MotionPhase,
    advance_joint,
    motion_phase,
    stopping_distance_rad,
)


def test_joint_accelerates_toward_a_distant_target() -> None:
    config = JointMotionConfig(max_speed_rad_s=2.0, acceleration_rad_s2=6.0)
    state = JointMotionState(angle_rad=0.0, speed_rad_s=0.0)

    assert motion_phase(state, target_rad=1.0, config=config) is MotionPhase.ACCELERATE
    advanced = advance_joint(state, target_rad=1.0, dt_s=0.1, config=config)

    assert advanced.speed_rad_s == pytest.approx(0.6)
    assert advanced.angle_rad == pytest.approx(0.06)


def test_joint_brakes_when_target_is_within_stopping_distance() -> None:
    config = JointMotionConfig(acceleration_rad_s2=2.0)
    state = JointMotionState(angle_rad=0.0, speed_rad_s=1.0)
    target_rad = 0.2

    assert stopping_distance_rad(state.speed_rad_s, config.acceleration_rad_s2) == 0.25
    assert motion_phase(state, target_rad, config) is MotionPhase.BRAKE


def test_joint_stops_exactly_at_target_instead_of_overshooting() -> None:
    config = JointMotionConfig(max_speed_rad_s=2.0, acceleration_rad_s2=1.0)
    state = JointMotionState(angle_rad=0.99, speed_rad_s=1.0)

    advanced = advance_joint(state, target_rad=1.0, dt_s=0.1, config=config)

    assert advanced == JointMotionState(angle_rad=1.0, speed_rad_s=0.0)
