import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

import { AppShell } from './AppShell'
import type { AppPage } from './AppShell'
import { ArmVideo } from './ArmVideo'
import { ConfigForm } from './ConfigForm'
import { MotionGuide } from './MotionGuide'
import { SolverStatus } from './SolverStatus'
import { useArmSession } from './useArmSession'
import { useArmVideo } from './useArmVideo'

export default function App() {
  const [page, setPage] = useState<AppPage>('live')
  const { stream } = useArmVideo()
  const {
    state,
    solver,
    error,
    sendTarget,
    saveMotionConfig,
    isTargetPending,
    isMotionConfigPending,
  } = useArmSession()

  return (
    <AppShell
      page={page}
      onPageChange={setPage}
      sidebar={
        <div className="flex flex-col gap-6">
          <ConfigForm
            target={state?.target ?? null}
            motion={state?.motion ?? null}
            onUpdateTarget={sendTarget}
            onUpdateMotionConfig={saveMotionConfig}
            isTargetPending={isTargetPending}
            isMotionConfigPending={isMotionConfigPending}
          />
          <div className="px-4">
            <Separator className="mb-6" />
            <SolverStatus result={solver} state={state} error={error} />
          </div>
        </div>
      }
    >
      {page === 'motion' ? (
        <MotionGuide />
      ) : (
        <Card className="min-h-0 flex-1 gap-0 py-0">
          <CardHeader className="shrink-0 border-b py-3">
            <CardTitle>Arm feed</CardTitle>
            <CardDescription>
              Live WebRTC stream from the solver. Disable your VPN if you cannot
              see the video feed.
            </CardDescription>
            <CardAction>
              <Badge variant={stream == null ? 'outline' : 'secondary'}>
                {stream == null ? 'Connecting' : 'Live'}
              </Badge>
            </CardAction>
          </CardHeader>
          <CardContent className="flex min-h-0 flex-1 flex-col overflow-hidden p-0">
            <ArmVideo stream={stream} onTarget={sendTarget} />
          </CardContent>
        </Card>
      )}
    </AppShell>
  )
}
