import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

import type { SolverResults } from './types'

type SolverStatusProps = {
  result: SolverResults | null
}

export function SolverStatus({ result }: SolverStatusProps) {
  if (result == null) {
    return <p className="text-sm text-muted-foreground">No solver result yet.</p>
  }

  return (
    <dl className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm tabular-nums">
      <div className="flex items-center gap-2">
        <dt className="text-muted-foreground">status</dt>
        <dd>
          <Badge variant={result.success ? 'secondary' : 'destructive'}>
            {result.success ? 'ok' : 'fail'}
          </Badge>
        </dd>
      </div>
      <div className="flex items-center gap-2">
        <dt className="text-muted-foreground">reason</dt>
        <dd className={cn(!result.success && 'text-destructive')}>{result.reason}</dd>
      </div>
      <div className="flex items-center gap-2">
        <dt className="text-muted-foreground">runtime</dt>
        <dd>{(result.runtime * 1000).toFixed(1)} ms</dd>
      </div>
      <div className="flex min-w-0 items-center gap-2">
        <dt className="text-muted-foreground">target</dt>
        <dd className="truncate">
          {result.target == null
            ? 'none'
            : `${result.target.x.toFixed(2)} m, ${result.target.y.toFixed(2)} m`}
        </dd>
      </div>
      <div className="flex min-w-0 items-center gap-2">
        <dt className="text-muted-foreground">solution</dt>
        <dd className="truncate">
          {result.solution == null
            ? 'none'
            : result.solution.map((value) => value.toFixed(4)).join(', ')}
        </dd>
      </div>
    </dl>
  )
}
