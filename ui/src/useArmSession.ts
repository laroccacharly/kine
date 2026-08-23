import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import type {
  ArmState,
  JointMotionConfig,
  SolverResults,
  TargetCommand,
  TargetUpdateResponse,
} from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init)
  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }
  return (await response.json()) as T
}

const jsonHeaders = { 'Content-Type': 'application/json' }
const armQueryKey = ['arm'] as const

function errorMessage(reason: unknown): string | null {
  if (reason == null) {
    return null
  }
  return reason instanceof Error ? reason.message : 'Request failed'
}

export function useArmSession() {
  const queryClient = useQueryClient()
  const armQuery = useQuery({
    queryKey: armQueryKey,
    queryFn: ({ signal }) => request<ArmState>('/api/arm', { signal }),
  })

  const targetMutation = useMutation({
    mutationFn: (target: TargetCommand) =>
      request<TargetUpdateResponse>('/api/arm/target', {
        method: 'PUT',
        headers: jsonHeaders,
        body: JSON.stringify(target),
      }),
    onSuccess: (next) => {
      queryClient.setQueryData(armQueryKey, next.state)
    },
  })

  const motionMutation = useMutation({
    mutationFn: (motion: JointMotionConfig) =>
      request<ArmState>('/api/arm/motion-config', {
        method: 'PUT',
        headers: jsonHeaders,
        body: JSON.stringify(motion),
      }),
    onSuccess: (next) => {
      queryClient.setQueryData(armQueryKey, next)
    },
  })

  function sendTarget(target: TargetCommand) {
    motionMutation.reset()
    targetMutation.mutate(target)
  }

  function sendMotion(motion: JointMotionConfig) {
    targetMutation.reset()
    motionMutation.mutate(motion)
  }

  const state = armQuery.data ?? null
  const solver: SolverResults | null = targetMutation.data?.solver ?? null
  const error = errorMessage(
    targetMutation.error ?? motionMutation.error ?? (state == null ? armQuery.error : null),
  )

  return { state, solver, error, sendTarget, sendMotion }
}
