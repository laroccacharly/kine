from pydantic import BaseModel

from kine.types import JointAngles


class TwoJointArm(BaseModel):
    l1: float
    l2: float
    angles: JointAngles = JointAngles(theta1=0.0, theta2=0.0)
    t_s: float = 0.0
    speed1_rad_s: float = 0.0
    speed2_rad_s: float = 0.0
