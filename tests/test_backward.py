import pytest

from kine.arm import TwoJointArm
from kine.solve import solve_forward, solve_inverse
from kine.types import JointAngles, TipPosition


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
    result = solve_inverse(arm, position)
    assert result.success
    assert result.solution is not None
    reached = solve_forward(
        arm, JointAngles(theta1=result.solution[0], theta2=result.solution[1])
    )
    assert reached.success
    assert reached.solution is not None
    assert TipPosition(x=reached.solution[0], y=reached.solution[1]) == position
