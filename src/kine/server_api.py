from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from kine.motion import JointMotionConfig
from kine.render import PixelPoint, world_point_from_frame_pixel
from kine.session import ArmSession
from kine.solve import SolverResults
from kine.types import TipPosition


class WorldTargetCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class PixelTargetCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x_px: float
    y_px: float


TargetCommand = WorldTargetCommand | PixelTargetCommand


class ArmState(BaseModel):
    target: TipPosition
    motion: JointMotionConfig


class TargetUpdateResponse(BaseModel):
    state: ArmState
    solver: SolverResults


def arm_state(session: ArmSession) -> ArmState:
    return ArmState(target=session.target, motion=session.motion_config)


def target_from_command(command: TargetCommand, session: ArmSession) -> TipPosition:
    if isinstance(command, WorldTargetCommand):
        return TipPosition(x=command.x, y=command.y)
    world = world_point_from_frame_pixel(
        PixelPoint(x_px=command.x_px, y_px=command.y_px),
        session.current_arm(),
        session.render_config,
    )
    return TipPosition(x=world.x_m, y=world.y_m)


def register_arm_routes(app: FastAPI, session: ArmSession) -> None:
    @app.get("/api/arm")
    async def get_arm() -> ArmState:
        return arm_state(session)

    @app.put("/api/arm/target")
    async def set_target(command: TargetCommand) -> TargetUpdateResponse:
        result = session.set_target(target_from_command(command, session))
        return TargetUpdateResponse(state=arm_state(session), solver=result)

    @app.put("/api/arm/motion-config")
    async def set_motion_config(config: JointMotionConfig) -> ArmState:
        session.set_motion_config(config)
        return arm_state(session)
