import pytest

from kine.two_joint import JointAngles, TipPosition, TwoJointArm


@pytest.mark.parametrize(
    "position",
    [
        TipPosition(x=2.0, y=0.0),
        TipPosition(x=0.0, y=2.0),
        TipPosition(x=1.0, y=1.0),
        TipPosition(x=-2.0, y=0.0),
    ],
)
def test_set_target_reaches_tip_position(position: TipPosition) -> None:
    arm = TwoJointArm(l1=1.0, l2=1.0)
    result = arm.set_target(position)
    assert result.success
    assert result.solution is not None
    reached = arm.tip_position(
        JointAngles(theta1=result.solution[0], theta2=result.solution[1])
    )
    assert reached.success
    assert reached.solution is not None
    assert TipPosition(x=reached.solution[0], y=reached.solution[1]) == position
