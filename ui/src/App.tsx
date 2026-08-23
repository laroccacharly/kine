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

import { ArmVideo } from './ArmVideo'
import { MotionForm } from './MotionForm'
import { SolverStatus } from './SolverStatus'
import { TargetForm } from './TargetForm'
import { useArmSession } from './useArmSession'
import { useArmVideo } from './useArmVideo'

export default function App() {
  const { stream } = useArmVideo()
  const { state, solver, error, sendTarget, sendMotion } = useArmSession()

  return (
    <div className="flex h-svh flex-col overflow-hidden">
      <header className="flex shrink-0 flex-wrap items-center justify-between gap-4 border-b px-5 py-3">
        <div className="flex flex-col gap-1">
          <h1 className="font-heading text-lg font-medium tracking-tight">Kine</h1>
          <p className="text-sm text-muted-foreground">Inverse kinematics camera feed</p>
        </div>
        <div className="flex flex-wrap items-end gap-6">
          <TargetForm onSubmit={sendTarget} />
          <MotionForm motion={state?.motion ?? null} onSubmit={sendMotion} />
        </div>
      </header>
      <main className="flex min-h-0 flex-1 flex-col p-3 sm:p-4">
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
      </main>
    </div>
  )
}
