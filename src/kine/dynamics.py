from pydantic import BaseModel, Field


class UniformLink(BaseModel):
    length_m: float = Field(gt=0)
    density_kg_per_m3: float = Field(gt=0)
    cross_section_m2: float = Field(gt=0)

    @property
    def mass_kg(self) -> float:
        return self.density_kg_per_m3 * self.cross_section_m2 * self.length_m


class MotorCommand(BaseModel):
    voltage_v: float = 12.0


class IntegratorConfig(BaseModel):
    dt_s: float = Field(default=1e-4, gt=0)


class DCMotor(BaseModel):
    resistance_ohm: float = Field(gt=0)
    torque_constant_nm_per_a: float = Field(gt=0)
    back_emf_constant_v_s_per_rad: float = Field(gt=0)

    def current_a(self, voltage_v: float, speed_rad_s: float) -> float:
        return (
            voltage_v - self.back_emf_constant_v_s_per_rad * speed_rad_s
        ) / self.resistance_ohm

    def torque_nm(self, voltage_v: float, speed_rad_s: float) -> float:
        return self.torque_constant_nm_per_a * self.current_a(voltage_v, speed_rad_s)

    def equilibrium_speed_rad_s(self, voltage_v: float) -> float:
        return voltage_v / self.back_emf_constant_v_s_per_rad


class LockedElbowSpin(BaseModel):
    """Two identical links of length l (reach 2l), elbow locked straight, no gravity."""

    link: UniformLink
    motor: DCMotor

    def inertia_about_base_kg_m2(self) -> float:
        mass_kg = self.link.mass_kg
        length_m = self.link.length_m
        return (8.0 / 3.0) * mass_kg * length_m * length_m

    def acceleration_rad_s2(self, voltage_v: float, speed_rad_s: float) -> float:
        torque_nm = self.motor.torque_nm(voltage_v, speed_rad_s)
        return torque_nm / self.inertia_about_base_kg_m2()

    def mechanical_time_constant_s(self) -> float:
        return (
            self.inertia_about_base_kg_m2()
            * self.motor.resistance_ohm
            / (
                self.motor.torque_constant_nm_per_a
                * self.motor.back_emf_constant_v_s_per_rad
            )
        )


def spin_speed_after_s(
    spin: LockedElbowSpin,
    command: MotorCommand,
    duration_s: float,
    integrator: IntegratorConfig,
) -> float:
    speed_rad_s = 0.0
    elapsed_s = 0.0
    while elapsed_s < duration_s:
        speed_rad_s += spin.acceleration_rad_s2(command.voltage_v, speed_rad_s) * integrator.dt_s
        elapsed_s += integrator.dt_s
    return speed_rad_s
