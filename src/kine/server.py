from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from kine.arm import TwoJointArm
from kine.arm_api import router as arm_router
from kine.motion import JointMotionConfig
from kine.render import RenderConfig
from kine.session import ArmSession
from kine.signaling import router as signaling_router
from kine.ui import UI


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
    app.include_router(arm_router)
    app.include_router(signaling_router)
    if ui is not None and ui.assets_exist():
        app.mount("/", StaticFiles(directory=str(ui.dist_dir), html=True), name="ui")
    return app


def create_default_session() -> ArmSession:
    return ArmSession(TwoJointArm(l1=1.0, l2=1.0), JointMotionConfig(), RenderConfig())
