import asyncio
import json
import socket
import threading
import time

import uvicorn
from aiortc import RTCSessionDescription
from websockets.asyncio.client import connect

from kine.server import create_app, create_local_peer_connection

FIRST_FRAME_TIMEOUT_S = 30


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ServerThread:
    def __init__(self) -> None:
        self.port = free_port()
        self.server = uvicorn.Server(
            uvicorn.Config(
                create_app(),
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
            )
        )
        self.server.install_signal_handlers = False
        self.thread = threading.Thread(target=self.server.run, daemon=True)

    def start(self) -> None:
        self.thread.start()
        deadline = time.monotonic() + 10
        while not self.server.started:
            if not self.thread.is_alive():
                raise RuntimeError("uvicorn exited before becoming ready")
            if time.monotonic() > deadline:
                raise TimeoutError("uvicorn did not start")
            time.sleep(0.01)

    def stop(self) -> None:
        self.server.should_exit = True
        self.thread.join(timeout=5)


async def receive_first_frame(ws_url: str):
    pc = create_local_peer_connection()
    pc.addTransceiver("video", direction="recvonly")
    first_frame: asyncio.Future = asyncio.get_running_loop().create_future()

    @pc.on("track")
    def on_track(track) -> None:
        async def read_first() -> None:
            frame = await track.recv()
            if not first_frame.done():
                first_frame.set_result(frame)

        asyncio.create_task(read_first())

    try:
        async with connect(ws_url) as websocket:
            message = json.loads(await websocket.recv())
            if message["type"] != "offer":
                raise AssertionError(f"expected offer, got {message['type']}")
            await pc.setRemoteDescription(
                RTCSessionDescription(sdp=message["sdp"], type="offer")
            )
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await websocket.send(json.dumps({"type": "answer", "sdp": pc.localDescription.sdp}))
            return await asyncio.wait_for(first_frame, timeout=FIRST_FRAME_TIMEOUT_S)
    finally:
        await pc.close()


def test_time_to_first_frame(record_property) -> None:
    server = ServerThread()
    started_at = time.perf_counter()
    server.start()
    server_ready_s = time.perf_counter() - started_at
    try:
        connect_started_at = time.perf_counter()
        frame = asyncio.run(receive_first_frame(f"ws://127.0.0.1:{server.port}/ws/signaling"))
        time_to_first_frame_s = time.perf_counter() - connect_started_at
    finally:
        server.stop()

    record_property("server_ready_s", server_ready_s)
    record_property("time_to_first_frame_s", time_to_first_frame_s)
    print(f"server_ready_s={server_ready_s:.3f}")
    print(f"time_to_first_frame_s={time_to_first_frame_s:.3f}")

    assert frame.width == 640
    assert frame.height == 480
    assert time_to_first_frame_s < FIRST_FRAME_TIMEOUT_S
