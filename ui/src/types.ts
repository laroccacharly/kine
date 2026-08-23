export type WorldTarget = {
  x: number
  y: number
}

export type TargetCommand = WorldTarget | { x_px: number; y_px: number }

export type JointMotionConfig = {
  max_speed_rad_s: number
  acceleration_rad_s2: number
  settle_rad: number
}

export type TipPosition = {
  x: number
  y: number
}

export type ArmState = {
  target: TipPosition
  motion: JointMotionConfig
}

export type SolverResults = {
  success: boolean
  solution: number[] | null
  reason: string
  runtime: number
}

export type TargetUpdateResponse = {
  state: ArmState
  solver: SolverResults
}
