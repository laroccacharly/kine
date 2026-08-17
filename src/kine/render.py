from math import cos, sin

from PIL import Image, ImageDraw
from pydantic import BaseModel

from kine.types import TipPosition, TwoJointArm


class RenderConfig(BaseModel):
    frame_width_px: int = 640
    frame_height_px: int = 480
    radius_px: int = 10
    padding_px: int = 16
    link_width_px: int = 8
    target_outline_width_px: int = 2
    background_rgb: tuple[int, int, int] = (18, 18, 22)
    target_rgb: tuple[int, int, int] = (120, 180, 255)
    link_rgb: tuple[int, int, int] = (220, 220, 230)
    joint_rgb: tuple[int, int, int] = (200, 80, 80)


class WorldPoint(BaseModel):
    x_m: float
    y_m: float


class PixelPoint(BaseModel):
    x_px: float
    y_px: float


def joint_positions_m(arm: TwoJointArm) -> list[WorldPoint]:
    elbow_x_m = arm.l1 * cos(arm.angles.theta1)
    elbow_y_m = arm.l1 * sin(arm.angles.theta1)
    tip_x_m = elbow_x_m + arm.l2 * cos(arm.angles.theta1 + arm.angles.theta2)
    tip_y_m = elbow_y_m + arm.l2 * sin(arm.angles.theta1 + arm.angles.theta2)
    return [
        WorldPoint(x_m=0.0, y_m=0.0),
        WorldPoint(x_m=elbow_x_m, y_m=elbow_y_m),
        WorldPoint(x_m=tip_x_m, y_m=tip_y_m),
    ]


def arm_pixels_per_meter(arm: TwoJointArm, config: RenderConfig) -> float:
    reach_m = arm.l1 + arm.l2
    if reach_m <= 0:
        raise ValueError("arm reach must be positive")
    half_min_side_px = min(config.frame_width_px, config.frame_height_px) / 2
    usable_radius_px = half_min_side_px - config.radius_px - config.padding_px
    return usable_radius_px / reach_m


def meters_to_pixels(point: WorldPoint, origin: PixelPoint, px_per_m: float) -> PixelPoint:
    return PixelPoint(
        x_px=origin.x_px + point.x_m * px_per_m,
        y_px=origin.y_px - point.y_m * px_per_m,
    )


def circle_bbox(center: PixelPoint, radius_px: float) -> tuple[float, float, float, float]:
    return (
        center.x_px - radius_px,
        center.y_px - radius_px,
        center.x_px + radius_px,
        center.y_px + radius_px,
    )


def render_arm(arm: TwoJointArm, target: TipPosition, config: RenderConfig) -> Image.Image:
    image = Image.new("RGB", (config.frame_width_px, config.frame_height_px), config.background_rgb)
    draw = ImageDraw.Draw(image)
    origin_px = PixelPoint(x_px=config.frame_width_px / 2, y_px=config.frame_height_px / 2)
    px_per_m = arm_pixels_per_meter(arm, config)

    joints_px = [
        meters_to_pixels(point_m, origin_px, px_per_m)
        for point_m in joint_positions_m(arm)
    ]
    target_px = meters_to_pixels(
        WorldPoint(x_m=target.x, y_m=target.y),
        origin_px,
        px_per_m,
    )

    draw.ellipse(
        circle_bbox(target_px, config.radius_px),
        outline=config.target_rgb,
        width=config.target_outline_width_px,
    )
    draw.line(
        [(point.x_px, point.y_px) for point in joints_px],
        fill=config.link_rgb,
        width=config.link_width_px,
    )
    for joint_px in joints_px:
        draw.ellipse(circle_bbox(joint_px, config.radius_px), fill=config.joint_rgb)
    return image
