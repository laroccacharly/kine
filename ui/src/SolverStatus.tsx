import type { SolverResults } from './types'

type SolverStatusProps = {
  result: SolverResults | null
}

export function SolverStatus({ result }: SolverStatusProps) {
  if (result == null) {
    return null
  }

  return (
    <dl className={result.success ? 'solver ok' : 'solver fail'}>
      <div>
        <dt>success</dt>
        <dd>{String(result.success)}</dd>
      </div>
      <div>
        <dt>reason</dt>
        <dd>{result.reason}</dd>
      </div>
      <div>
        <dt>runtime</dt>
        <dd>{(result.runtime * 1000).toFixed(1)} ms</dd>
      </div>
      <div>
        <dt>solution</dt>
        <dd>
          {result.solution == null
            ? 'none'
            : result.solution.map((value) => value.toFixed(4)).join(', ')}
        </dd>
      </div>
    </dl>
  )
}
