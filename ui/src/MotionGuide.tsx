import { ArrowRightIcon } from 'lucide-react'

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

const phases = [
  {
    name: '1. Accelerate',
    range: '0.00–0.25 rad',
    speed: '0 → 1 rad/s',
    acceleration: '+2 rad/s²',
    width: 'w-1/4',
    color: 'bg-emerald-500/15 text-emerald-800 dark:text-emerald-300',
  },
  {
    name: '2. Cruise',
    range: '0.25–0.75 rad',
    speed: '1 rad/s',
    acceleration: '0 rad/s²',
    width: 'w-1/2',
    color: 'bg-sky-500/15 text-sky-800 dark:text-sky-300',
  },
  {
    name: '3. Brake',
    range: '0.75–1.00 rad',
    speed: '1 → 0 rad/s',
    acceleration: '−2 rad/s²',
    width: 'w-1/4',
    color: 'bg-amber-500/20 text-amber-900 dark:text-amber-300',
  },
]

export function MotionGuide() {
  return (
    <div className="mx-auto w-full max-w-5xl space-y-4 overflow-y-auto pb-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">How joint motion works</h1>
        <p className="mt-1 max-w-3xl text-sm text-muted-foreground">
          Each joint independently decides whether to accelerate, cruise, or brake on
          every 1/60-second trajectory step.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>One-joint example</CardTitle>
          <CardDescription>
            Move 1 radian from rest with a 1 rad/s speed limit and 2 rad/s² acceleration.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <div className="mb-2 flex justify-between font-mono text-xs text-muted-foreground">
              <span>0 rad</span>
              <span>target: 1 rad</span>
            </div>
            <div
              className="flex h-16 overflow-hidden rounded-lg ring-1 ring-foreground/10"
              aria-label="Motion phases from zero to one radian"
            >
              {phases.map((phase) => (
                <div
                  key={phase.name}
                  className={`${phase.width} ${phase.color} flex items-center justify-center border-r px-2 text-center text-xs font-medium last:border-r-0 sm:text-sm`}
                >
                  {phase.name}
                </div>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-2xl text-left text-sm">
              <thead className="bg-muted/60 text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Phase</th>
                  <th className="px-4 py-3 font-medium">Position</th>
                  <th className="px-4 py-3 font-medium">Speed</th>
                  <th className="px-4 py-3 font-medium">Applied acceleration</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {phases.map((phase) => (
                  <tr key={phase.name}>
                    <td className="px-4 py-3 font-medium">{phase.name}</td>
                    <td className="px-4 py-3 font-mono text-xs">{phase.range}</td>
                    <td className="px-4 py-3 font-mono text-xs">{phase.speed}</td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {phase.acceleration}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>When braking starts</CardTitle>
            <CardDescription>The joint continually asks whether it can still stop in time.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-lg bg-muted p-4 text-center font-mono text-sm">
              stopping distance = speed² / (2 × acceleration)
            </div>
            <div className="flex items-center justify-center gap-2 text-sm">
              <span>1² / (2 × 2)</span>
              <ArrowRightIcon className="size-4 text-muted-foreground" />
              <strong>0.25 rad</strong>
            </div>
            <p className="text-sm leading-6 text-muted-foreground">
              At maximum speed, braking therefore starts 0.25 rad before the target:
              at position 0.75 rad.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>What braking does</CardTitle>
            <CardDescription>Acceleration points opposite the current joint speed.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="rounded-lg bg-muted p-4 text-center font-mono text-sm">
              new speed = speed + acceleration × Δt
            </div>
            <p className="text-sm leading-6 text-muted-foreground">
              With −2 rad/s² applied every 0.1 seconds, speed falls from 1.0 to 0.8,
              0.6, 0.4, 0.2, and finally 0 rad/s at the target.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
