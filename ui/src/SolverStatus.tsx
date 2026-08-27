import type { ReactNode } from 'react'

import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

import type { ArmState, SolverResults } from './types'

type SolverStatusProps = {
  result: SolverResults | null
  state: ArmState | null
  error: string | null
}

function Metric({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className="mt-0.5 font-mono text-sm tabular-nums">{children}</dd>
    </div>
  )
}

function ValueList({ values }: { values: string[] }) {
  return (
    <div className="grid grid-cols-2 gap-x-2 gap-y-0.5">
      {values.map((value, index) => (
        <span key={index} className="whitespace-nowrap">
          {value}
        </span>
      ))}
    </div>
  )
}

export function SolverStatus({ result, state, error }: SolverStatusProps) {
  return (
    <section aria-labelledby="solver-results-heading">
      <h2 id="solver-results-heading" className="mb-3 text-sm font-medium">
        Solver results
      </h2>
      {error != null ? (
        <p className="text-sm text-destructive">{error}</p>
      ) : result == null ? (
        <p className="text-sm text-muted-foreground">No solver result yet.</p>
      ) : (
        <dl className="flex flex-col gap-3">
          <div className="grid grid-cols-2 gap-3">
            <Metric label="status">
              <Badge variant={result.success ? 'secondary' : 'destructive'}>
                {result.success ? 'ok' : 'fail'}
              </Badge>
            </Metric>
            <Metric label="runtime">{(result.runtime * 1000).toFixed(1)} ms</Metric>
          </div>
          <Metric label="reason">
            <span className={cn(!result.success && 'text-destructive')}>{result.reason}</span>
          </Metric>
          <Metric label="target">
            {state == null ? (
              'none'
            ) : (
              <ValueList
                values={[`${state.target.x.toFixed(2)} m`, `${state.target.y.toFixed(2)} m`]}
              />
            )}
          </Metric>
          <Metric label="motion">
            {state == null ? (
              'none'
            ) : (
              <ValueList
                values={[
                  `${state.motion.max_speed_rad_s} rad/s`,
                  `${state.motion.acceleration_rad_s2} rad/s²`,
                ]}
              />
            )}
          </Metric>
          <Metric label="solution">
            {result.solution == null ? (
              'none'
            ) : (
              <ValueList values={result.solution.map((value) => value.toFixed(4))} />
            )}
          </Metric>
        </dl>
      )}
    </section>
  )
}
