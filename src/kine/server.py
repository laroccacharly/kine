import numpy as np
from aiortc import (
    RTCConfiguration,
    RTCIceCandidate,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from aiortc.sdp import candidate_from_sdp
from av import VideoFrame
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig
from kine.render import PixelPoint, RenderConfig, render_arm, world_point_from_frame_pixel
from kine.session import ArmSession
from kine.solve import SolverResults
from kine.types import TipPosition
from kine.ui import UI


def create_local_peer_connection() -> RTCPeerConnection:
    return RTCPeerConnection(
        RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )


def create_ui_app() -> FastAPI:
    return create_app(UI())


def create_app(ui: UI | None = None, session: ArmSession | None = None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    session = session or ArmSession(
        TwoJointArm(l1=1.0, l2=1.0), JointMotionConfig(), RenderConfig()
    )
    app.state.arm_session = session
    register_routes(app, session)
    if ui is not None and ui.assets_exist():
        app.mount("/", StaticFiles(directory=str(ui.dist_dir), html=True), name="ui")
    return app


class BrowserIceCandidate(BaseModel):
    candidate: str
    sdpMid: str | None = None
    sdpMLineIndex: int | None = None


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


def ice_candidate_from_browser(data: BrowserIceCandidate) -> RTCIceCandidate:
    sdp = data.candidate.removeprefix("candidate:")
    candidate = candidate_from_sdp(sdp)
    candidate.sdpMid = data.sdpMid
    candidate.sdpMLineIndex = data.sdpMLineIndex
    return candidate


class ArmVideoTrack(VideoStreamTrack):
    def __init__(self, session: ArmSession) -> None:
        super().__init__()
        self.session = session

    async def recv(self) -> VideoFrame:
        pts, time_base = await self.next_timestamp()
        frame = VideoFrame.from_ndarray(
            np.asarray(
                render_arm(
                    self.session.current_arm(),
                    self.session.target,
                    self.session.render_config,
                )
            ),
            format="rgb24",
        )
        frame.pts = pts
        frame.time_base = time_base
        return frame


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


def register_routes(app: FastAPI, session: ArmSession) -> None:
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

    @app.websocket("/ws/signaling")
    async def stream_arm(websocket: WebSocket) -> None:
        await websocket.accept()
        pc = create_local_peer_connection()
        track = ArmVideoTrack(session)
        pc.addTrack(track)
        try:
            await pc.setLocalDescription(await pc.createOffer())
            await websocket.send_json({"type": "offer", "sdp": pc.localDescription.sdp})
            while True:
                message = await websocket.receive_json()
                kind = message["type"]
                if kind == "answer":
                    await pc.setRemoteDescription(
                        RTCSessionDescription(sdp=message["sdp"], type="answer")
                    )
                    continue
                if kind != "ice":
                    continue
                payload = message.get("candidate")
                if not payload or not payload.get("candidate"):
                    continue
                await pc.addIceCandidate(ice_candidate_from_browser(BrowserIceCandidate(**payload)))
        except WebSocketDisconnect:
            pass
        finally:
            await pc.close()
