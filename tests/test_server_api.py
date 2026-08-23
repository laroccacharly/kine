from fastapi.testclient import TestClient

from kine.arm import TwoJointArm
from kine.motion import JointMotionConfig
from kine.render import RenderConfig
from kine.server import create_app
from kine.session import ArmSession


def test_rest_controls_update_the_application_arm() -> None:
    session = ArmSession(TwoJointArm(l1=1.0, l2=1.0), JointMotionConfig(), RenderConfig())
    app = create_app(session=session)
    config = {
        "max_speed_rad_s": 1.25,
        "acceleration_rad_s2": 3.5,
        "settle_rad": 0.001,
    }

    with TestClient(app) as client:
        response = client.put("/api/arm/motion-config", json=config)
        target_response = client.put("/api/arm/target", json={"x": 1.0, "y": 1.0})
        state = client.get("/api/arm")

    assert response.status_code == 200
    assert response.json()["motion"] == config
    assert target_response.status_code == 200
    assert target_response.json()["solver"]["success"] is True
    assert target_response.json()["state"]["target"] == {"x": 1.0, "y": 1.0}
    assert state.json()["motion"] == config
    assert state.json()["target"] == {"x": 1.0, "y": 1.0}
    assert app.state.arm_session is session


def test_target_command_requires_one_complete_coordinate_system() -> None:
    app = create_app()

    with TestClient(app) as client:
        missing_coordinate = client.put("/api/arm/target", json={"x": 1.0})
        mixed_coordinates = client.put(
            "/api/arm/target",
            json={"x": 1.0, "y": 0.0, "x_px": 320.0, "y_px": 240.0},
        )

    assert missing_coordinate.status_code == 422
    assert mixed_coordinates.status_code == 422
