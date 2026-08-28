"""Render a deterministic, non-default video frame for the project README."""

from argparse import ArgumentParser
from math import cos, pi, sin
from pathlib import Path
from random import Random

from kine.arm import TwoJointArm
from kine.render import RenderConfig, render_arm
from kine.types import JointAngles, TipPosition

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "robot-frame.png"
DEFAULT_SEED = 20260828


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    random = Random(args.seed)
    arm = TwoJointArm(
        l1=1.0,
        l2=1.0,
        angles=JointAngles(
            theta1=random.uniform(0.25 * pi, 0.75 * pi),
            theta2=random.uniform(-0.9 * pi, 0.9 * pi),
        ),
    )
    target_radius = random.uniform(0.65, 1.65)
    target_angle = random.uniform(-pi, pi)
    target = TipPosition(
        x=target_radius * cos(target_angle),
        y=target_radius * sin(target_angle),
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    render_arm(arm, target, RenderConfig()).save(args.output)
    print(f"saved deterministic frame to {args.output}")


if __name__ == "__main__":
    main()
