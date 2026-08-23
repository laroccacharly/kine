import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame

from kine.render import render_arm
from kine.session import ArmSession


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
