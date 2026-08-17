from math import cos, sin

import numpy as np
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.sdp import candidate_from_sdp
from av import VideoFrame
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw
from pydantic import BaseModel

from kine.solve import SolverResults
from kine.types import JointAngles, TipPosition, TwoJointArm
from kine.ui import UI

WIDTH = 640
HEIGHT = 480


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


def render_arm(arm: TwoJointArm, angles: JointAngles, target: TipPosition) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 22))
    draw = ImageDraw.Draw(image)
    cx = WIDTH / 2
    cy = HEIGHT / 2
    scale = min(WIDTH, HEIGHT) * 0.35
    x1 = arm.l1 * cos(angles.theta1)
    y1 = arm.l1 * sin(angles.theta1)
    x2 = x1 + arm.l2 * cos(angles.theta1 + angles.theta2)
    y2 = y1 + arm.l2 * sin(angles.theta1 + angles.theta2)

    def px(x: float, y: float) -> tuple[float, float]:
        return cx + x * scale, cy - y * scale

    joints = [px(0.0, 0.0), px(x1, y1), px(x2, y2)]
    target_px = px(target.x, target.y)
    r_target = 7
    draw.ellipse(
        (
            target_px[0] - r_target,
            target_px[1] - r_target,
            target_px[0] + r_target,
            target_px[1] + r_target,
        ),
        outline=(120, 180, 255),
        width=2,
    )
    draw.line(joints, fill=(220, 220, 230), width=8)
    for point in joints:
        r = 10
        draw.ellipse(
            (point[0] - r, point[1] - r, point[0] + r, point[1] + r),
            fill=(200, 80, 80),
        )
    return image


class ArmVideoTrack(VideoStreamTrack):
    def __init__(self, arm: TwoJointArm) -> None:
        super().__init__()
        self.arm = arm
        self.target = TipPosition(x=2.0, y=0.0)
        self.angles = JointAngles(theta1=0.0, theta2=0.0)
        result = arm.joint_angles(self.target)
        if result.success and result.solution is not None:
            self.angles = JointAngles(theta1=result.solution[0], theta2=result.solution[1])

    def set_target(self, target: TipPosition) -> SolverResults:
        self.target = target
        result = self.arm.joint_angles(target)
        if result.success and result.solution is not None:
            self.angles = JointAngles(theta1=result.solution[0], theta2=result.solution[1])
        return result

    async def recv(self) -> VideoFrame:
        pts, time_base = await self.next_timestamp()
        frame = VideoFrame.from_ndarray(
            np.asarray(render_arm(self.arm, self.angles, self.target)), format="rgb24"
        )
        frame.pts = pts
        frame.time_base = time_base
        return frame


def register_routes(app: FastAPI) -> None:
    @app.websocket("/ws")
    async def stream_arm(websocket: WebSocket) -> None:
        await websocket.accept()
        pc = RTCPeerConnection()
        arm = TwoJointArm(l1=1.0, l2=1.0)
        track = ArmVideoTrack(arm)
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
                    result = track.set_target(TipPosition(x=message["x"], y=message["y"]))
                    await websocket.send_json({"type": "solver", **result.model_dump()})
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
