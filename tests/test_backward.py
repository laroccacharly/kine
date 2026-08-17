from math import pi

import pytest

from kine.two_joint import JointAngles, TipPosition, TwoJointArm


@pytest.mark.parametrize(
    ("position", "valid_solutions"),
    [
        (TipPosition(x=2.0, y=0.0), [JointAngles(theta1=0.0, theta2=0.0)]),
        (TipPosition(x=0.0, y=2.0), [JointAngles(theta1=pi / 2, theta2=0.0)]),
        (
            TipPosition(x=1.0, y=1.0),
            [
                JointAngles(theta1=0.0, theta2=pi / 2),
                JointAngles(theta1=pi / 2, theta2=-pi / 2),
            ],
        ),
        (TipPosition(x=-2.0, y=0.0), [JointAngles(theta1=pi, theta2=0.0)]),
    ],
)
def test_joint_angles_for_tip_position(
    position: TipPosition,
    valid_solutions: list[JointAngles],
) -> None:
    arm = TwoJointArm(l1=1.0, l2=1.0)
    result = arm.joint_angles(position)
    assert result.success
    assert result.solution is not None
    assert JointAngles(theta1=result.solution[0], theta2=result.solution[1]) in valid_solutions
