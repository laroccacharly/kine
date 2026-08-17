import numpy as np
from aiortc import (
    RTCConfiguration,
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from aiortc.sdp import candidate_from_sdp
from av import VideoFrame
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from kine.motion import JointMotion, JointMotionConfig
from kine.render import PixelPoint, RenderConfig, render_arm, world_point_from_frame_pixel
from kine.solve import SolverResults
from kine.types import JointAngles, TipPosition, TwoJointArm
from kine.ui import UI


def create_local_peer_connection() -> RTCPeerConnection:
    """Create a peer connection that only advertises local network routes."""
    return RTCPeerConnection(RTCConfiguration(iceServers=[]))


def create_app(ui: UI | None = None) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routes(app)
    if ui is not None and ui.assets_exist():
        app.mount("/", StaticFiles(directory=str(ui.dist_dir), html=True), name="ui")
    return app


class TargetCommand(BaseModel):
    x: float | None = None
    y: float | None = None
    x_px: float | None = None
    y_px: float | None = None


class BrowserIceCandidate(BaseModel):
    candidate: str
    sdpMid: str | None = None
    sdpMLineIndex: int | None = None


def ice_candidate_from_browser(data: BrowserIceCandidate) -> RTCIceCandidate:
    sdp = data.candidate.removeprefix("candidate:")
    candidate = candidate_from_sdp(sdp)
    candidate.sdpMid = data.sdpMid
    candidate.sdpMLineIndex = data.sdpMLineIndex
    return candidate


class ArmVideoTrack(VideoStreamTrack):
    def __init__(
        self,
        arm: TwoJointArm,
        config: RenderConfig,
        motion_config: JointMotionConfig,
    ) -> None:
        super().__init__()
        self.arm = arm
        self.config = config
        self.time_s: float | None = None
        result = arm.set_target(arm.target)
        if result.success and result.solution is not None:
            self.arm.angles = JointAngles(theta1=result.solution[0], theta2=result.solution[1])
        self.motion = JointMotion.at_rest(self.arm.angles, motion_config)

    def set_target(self, target: TipPosition) -> SolverResults:
        result = self.arm.set_target(target)
        if result.success and result.solution is not None:
            self.motion.set_goal(JointAngles(theta1=result.solution[0], theta2=result.solution[1]))
        return result

    def set_target_from_command(self, command: TargetCommand) -> SolverResults | None:
        target = self.tip_from_command(command)
        if target is None:
            return None
        return self.set_target(target)

    def tip_from_command(self, command: TargetCommand) -> TipPosition | None:
        if command.x_px is not None and command.y_px is not None:
            world = world_point_from_frame_pixel(
                PixelPoint(x_px=command.x_px, y_px=command.y_px),
                self.arm,
                self.config,
            )
            return TipPosition(x=world.x_m, y=world.y_m)
        if command.x is None or command.y is None:
            return None
        return TipPosition(x=command.x, y=command.y)

    async def recv(self) -> VideoFrame:
        pts, time_base = await self.next_timestamp()
        now_s = float(pts * time_base)
        dt_s = 0.0 if self.time_s is None else now_s - self.time_s
        self.time_s = now_s
        self.arm.angles = self.motion.step(dt_s)
        frame = VideoFrame.from_ndarray(
            np.asarray(render_arm(self.arm, self.config)), format="rgb24"
        )
        frame.pts = pts
        frame.time_base = time_base
        return frame


def register_routes(app: FastAPI) -> None:
    @app.websocket("/ws")
    async def stream_arm(websocket: WebSocket) -> None:
        await websocket.accept()
        pc = create_local_peer_connection()
        arm = TwoJointArm(l1=1.0, l2=1.0)
        track = ArmVideoTrack(arm, RenderConfig(), JointMotionConfig())
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
                if kind == "target":
                    result = track.set_target_from_command(TargetCommand.model_validate(message))
                    if result is None:
                        continue
                    await websocket.send_json(
                        {
                            "type": "solver",
                            **result.model_dump(),
                            "target": track.arm.target.model_dump(),
                        }
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
