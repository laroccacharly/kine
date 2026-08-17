from math import pi

import pytest

from kine.two_joint import JointAngles, TipPosition, TwoJointArm


@pytest.mark.parametrize(
    ("angles", "expected"),
    [
        (JointAngles(theta1=0.0, theta2=0.0), TipPosition(x=2.0, y=0.0)),
        (JointAngles(theta1=pi / 2, theta2=0.0), TipPosition(x=0.0, y=2.0)),
        (JointAngles(theta1=0.0, theta2=pi / 2), TipPosition(x=1.0, y=1.0)),
        (JointAngles(theta1=pi / 2, theta2=pi), TipPosition(x=0.0, y=0.0)),
    ],
)
def test_tip_position_for_two_joint_angles(
    angles: JointAngles,
    expected: TipPosition,
) -> None:
    arm = TwoJointArm(l1=1.0, l2=1.0)
    position = arm.tip_position(angles)
    assert position == expected
