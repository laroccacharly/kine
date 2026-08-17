export type TargetCommand =
  | { x: number; y: number }
  | { x_px: number; y_px: number }

export type SolverResults = {
  success: boolean
  solution: number[] | null
  reason: string
  runtime: number
  target: { x: number; y: number } | null
}
