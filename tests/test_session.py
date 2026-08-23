import pytest

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig
from kine.render import RenderConfig
from kine.session import ArmSession


def test_motion_config_replans_without_solving_inverse(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = ArmSession(TwoJointArm(l1=1.0, l2=1.0), JointMotionConfig(), RenderConfig())
    goal = session.goal

    def fail_if_called(*args, **kwargs):
        raise AssertionError("changing motion config must not rerun inverse kinematics")

    monkeypatch.setattr("kine.session.solve_inverse", fail_if_called)
    config = JointMotionConfig(max_speed_rad_s=1.0, acceleration_rad_s2=2.0)

    session.set_motion_config(config)

    assert session.motion_config == config
    assert session.goal == goal
