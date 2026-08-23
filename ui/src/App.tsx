import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import { AppShell } from './AppShell'
import { ArmVideo } from './ArmVideo'
import { ConfigForm } from './ConfigForm'
import { SolverStatus } from './SolverStatus'
import { useArmSession } from './useArmSession'
import { useArmVideo } from './useArmVideo'

export default function App() {
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
      sidebar={
        <ConfigForm
          target={state?.target ?? null}
          motion={state?.motion ?? null}
          onUpdateTarget={sendTarget}
          onUpdateMotionConfig={saveMotionConfig}
          isTargetPending={isTargetPending}
          isMotionConfigPending={isMotionConfigPending}
        />
      }
    >
      <Card className="min-h-0 flex-1 gap-0 py-0">
        <CardHeader className="shrink-0 border-b py-3">
          <CardTitle>Arm feed</CardTitle>
          <CardDescription>Live WebRTC stream from the solver</CardDescription>
          <CardAction>
            <Badge variant={stream == null ? 'outline' : 'secondary'}>
              {stream == null ? 'Connecting' : 'Live'}
            </Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="flex min-h-0 flex-1 flex-col overflow-hidden p-0">
          <ArmVideo stream={stream} onTarget={sendTarget} />
        </CardContent>
        <CardFooter className="shrink-0 justify-start">
          <SolverStatus result={solver} state={state} error={error} />
        </CardFooter>
      </Card>
    </AppShell>
  )
}
