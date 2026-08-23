from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig
from kine.render import RenderConfig
from kine.server_api import (
    ArmState,
    PixelTargetCommand,
    TargetCommand,
    TargetUpdateResponse,
    WorldTargetCommand,
    arm_state,
    register_arm_routes,
    target_from_command,
)
from kine.session import ArmSession
from kine.ui import UI
from kine.webrtc import (
    ArmVideoTrack,
    BrowserIceCandidate,
    create_local_peer_connection,
    ice_candidate_from_browser,
    register_signaling_route,
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
    session = session or create_default_session()
    app.state.arm_session = session
    register_routes(app, session)
    if ui is not None and ui.assets_exist():
        app.mount("/", StaticFiles(directory=str(ui.dist_dir), html=True), name="ui")
    return app


def create_default_session() -> ArmSession:
    return ArmSession(TwoJointArm(l1=1.0, l2=1.0), JointMotionConfig(), RenderConfig())


def register_routes(app: FastAPI, session: ArmSession) -> None:
    register_arm_routes(app, session)
    register_signaling_route(app, session)


__all__ = [
    "ArmState",
    "ArmVideoTrack",
    "BrowserIceCandidate",
    "PixelTargetCommand",
    "TargetCommand",
    "TargetUpdateResponse",
    "WorldTargetCommand",
    "arm_state",
    "create_app",
    "create_default_session",
    "create_local_peer_connection",
    "create_ui_app",
    "ice_candidate_from_browser",
    "register_routes",
    "target_from_command",
]
