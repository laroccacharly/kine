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
import { MotionForm } from './MotionForm'
import { SolverStatus } from './SolverStatus'
import { TargetForm } from './TargetForm'
import { useArmSession } from './useArmSession'
import { useArmVideo } from './useArmVideo'

export default function App() {
  const { stream } = useArmVideo()
  const { state, solver, error, sendTarget, saveMotionConfig } = useArmSession()

  return (
    <AppShell
      sidebar={
        <div className="flex flex-col gap-6 px-4">
          <TargetForm onSubmit={sendTarget} />
          <MotionForm motion={state?.motion ?? null} onSubmit={saveMotionConfig} />
        </div>
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
