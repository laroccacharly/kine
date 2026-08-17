from pydantic import BaseModel


class JointAngles(BaseModel):
    theta1: float
    theta2: float


class TipPosition(BaseModel):
    x: float
    y: float


class TwoJointArm(BaseModel):
    l1: float
    l2: float

    def tip_position(self, angles: JointAngles) -> TipPosition:
        raise NotImplementedError

    def joint_angles(self, position: TipPosition) -> list[JointAngles]:
        raise NotImplementedError
