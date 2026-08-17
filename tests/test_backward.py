from math import pi

import pytest

from kine.two_joint import JointAngles, TipPosition, TwoJointArm


@pytest.mark.parametrize(
    ("position", "expected"),
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
    expected: list[JointAngles],
) -> None:
    arm = TwoJointArm(l1=1.0, l2=1.0)
    solutions = arm.joint_angles(position)
    assert len(solutions) == len(expected)
    for expected_angles in expected:
        assert any(
            solution.theta1 == pytest.approx(expected_angles.theta1)
            and solution.theta2 == pytest.approx(expected_angles.theta2)
            for solution in solutions
        )
