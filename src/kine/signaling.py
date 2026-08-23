from typing import Annotated, Literal

from aiortc import (
    RTCConfiguration,
    RTCIceCandidate,
    RTCIceServer,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.sdp import candidate_from_sdp
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from kine.arm_video import ArmVideoTrack
from kine.session import ArmSession

router = APIRouter(tags=["signaling"])


class BrowserIceCandidate(BaseModel):
    candidate: str
    sdpMid: str | None = None
    sdpMLineIndex: int | None = None


class AnswerMessage(BaseModel):
    type: Literal["answer"]
    sdp: str


class IceMessage(BaseModel):
    type: Literal["ice"]
    candidate: BrowserIceCandidate | None = None


SignalingMessage = Annotated[AnswerMessage | IceMessage, Field(discriminator="type")]
signaling_message_adapter = TypeAdapter(SignalingMessage)


def create_local_peer_connection() -> RTCPeerConnection:
    return RTCPeerConnection(
        RTCConfiguration(iceServers=[RTCIceServer(urls="stun:stun.l.google.com:19302")])
    )


def ice_candidate_from_browser(data: BrowserIceCandidate) -> RTCIceCandidate:
    candidate = candidate_from_sdp(data.candidate.removeprefix("candidate:"))
    candidate.sdpMid = data.sdpMid
    candidate.sdpMLineIndex = data.sdpMLineIndex
    return candidate


class SignalingSession:
    def __init__(
        self, arm_session: ArmSession, peer_connection: RTCPeerConnection | None = None
    ) -> None:
        self.peer_connection = peer_connection or create_local_peer_connection()
        self.peer_connection.addTrack(ArmVideoTrack(arm_session))

    async def run(self, websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            await self._send_offer(websocket)
            while True:
                try:
                    message = signaling_message_adapter.validate_python(
                        await websocket.receive_json()
                    )
                except ValidationError:
                    continue
                await self._handle(message)
        except WebSocketDisconnect:
            pass
        finally:
            await self.peer_connection.close()

    async def _send_offer(self, websocket: WebSocket) -> None:
        await self.peer_connection.setLocalDescription(
            await self.peer_connection.createOffer()
        )
        description = self.peer_connection.localDescription
        if description is None:
            raise RuntimeError("peer connection did not create a local description")
        await websocket.send_json({"type": "offer", "sdp": description.sdp})

    async def _handle(self, message: SignalingMessage) -> None:
        if isinstance(message, AnswerMessage):
            await self.peer_connection.setRemoteDescription(
                RTCSessionDescription(sdp=message.sdp, type="answer")
            )
        elif message.candidate is not None and message.candidate.candidate:
            await self.peer_connection.addIceCandidate(
                ice_candidate_from_browser(message.candidate)
            )


@router.websocket("/ws/signaling")
async def stream_arm(websocket: WebSocket) -> None:
    await SignalingSession(websocket.app.state.arm_session).run(websocket)
