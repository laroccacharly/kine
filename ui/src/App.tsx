import { ArmVideo } from './ArmVideo'
import { SolverStatus } from './SolverStatus'
import { TargetForm } from './TargetForm'
import { useArmStream } from './useArmStream'

export default function App() {
  const { videoRef, solver, sendTarget } = useArmStream()

  return (
    <main>
      <TargetForm onSubmit={sendTarget} />
      <SolverStatus result={solver} />
      <ArmVideo videoRef={videoRef} />
    </main>
  )
}
