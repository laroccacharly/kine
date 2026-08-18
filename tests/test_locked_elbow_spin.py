from math import exp

import pytest

from kine.dynamics import (
    DCMotor,
    IntegratorConfig,
    LockedElbowSpin,
    MotorCommand,
    UniformLink,
    spin_speed_after_s,
)


def aluminum_links() -> UniformLink:
    return UniformLink(
        length_m=0.5,
        density_kg_per_m3=2700.0,
        cross_section_m2=1e-4,
    )


def dc_motor() -> DCMotor:
    return DCMotor(
        resistance_ohm=1.0,
        torque_constant_nm_per_a=0.1,
        back_emf_constant_v_s_per_rad=0.1,
    )


def locked_spin(density_kg_per_m3: float | None = None) -> LockedElbowSpin:
    link = aluminum_links()
    if density_kg_per_m3 is not None:
        link = link.model_copy(update={"density_kg_per_m3": density_kg_per_m3})
    return LockedElbowSpin(link=link, motor=dc_motor())


def test_extended_arm_inertia_is_eight_thirds_m_l_squared() -> None:
    spin = locked_spin()
    mass_kg = spin.link.mass_kg
    length_m = spin.link.length_m
    assert mass_kg == 2700.0 * 1e-4 * 0.5
    assert spin.inertia_about_base_kg_m2() == (8.0 / 3.0) * mass_kg * length_m**2


def test_constant_voltage_has_zero_acceleration_at_back_emf_speed() -> None:
    spin = locked_spin()
    command = MotorCommand()
    speed_rad_s = spin.motor.equilibrium_speed_rad_s(command.voltage_v)
    assert speed_rad_s == command.voltage_v / spin.motor.back_emf_constant_v_s_per_rad
    assert spin.acceleration_rad_s2(command.voltage_v, speed_rad_s) == 0.0
    assert spin.motor.current_a(command.voltage_v, speed_rad_s) == 0.0
    assert spin.motor.torque_nm(command.voltage_v, speed_rad_s) == 0.0


def test_equilibrium_speed_does_not_depend_on_density() -> None:
    light = locked_spin(density_kg_per_m3=1000.0)
    heavy = locked_spin(density_kg_per_m3=8000.0)
    command = MotorCommand()
    assert light.motor.equilibrium_speed_rad_s(command.voltage_v) == heavy.motor.equilibrium_speed_rad_s(
        command.voltage_v
    )
    assert light.acceleration_rad_s2(
        command.voltage_v, light.motor.equilibrium_speed_rad_s(command.voltage_v)
    ) == 0.0
    assert heavy.acceleration_rad_s2(
        command.voltage_v, heavy.motor.equilibrium_speed_rad_s(command.voltage_v)
    ) == 0.0
    assert heavy.mechanical_time_constant_s() == 8.0 * light.mechanical_time_constant_s()


def test_speed_approaches_equilibrium_along_the_closed_form() -> None:
    spin = locked_spin()
    command = MotorCommand()
    integrator = IntegratorConfig()
    tau_s = spin.mechanical_time_constant_s()
    omega_eq = spin.motor.equilibrium_speed_rad_s(command.voltage_v)
    duration_s = tau_s
    simulated = spin_speed_after_s(spin, command, duration_s, integrator)
    expected = omega_eq * (1.0 - exp(-duration_s / tau_s))
    assert simulated == pytest.approx(expected, rel=1e-3)
