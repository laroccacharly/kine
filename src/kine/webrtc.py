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
from pydantic import BaseModel

from kine.render import render_arm
from kine.session import ArmSession


class BrowserIceCandidate(BaseModel):
    candidate: str
    sdpMid: str | None = None
    sdpMLineIndex: int | None = None


def create_local_peer_connection() -> RTCPeerConnection:
    return RTCPeerConnection(
        RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )


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


def register_signaling_route(app: FastAPI, session: ArmSession) -> None:
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
                candidate = BrowserIceCandidate(**payload)
                await pc.addIceCandidate(ice_candidate_from_browser(candidate))
        except WebSocketDisconnect:
            pass
        finally:
            await pc.close()
