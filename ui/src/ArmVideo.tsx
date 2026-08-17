import type { RefObject } from 'react'

type ArmVideoProps = {
  videoRef: RefObject<HTMLVideoElement | null>
}

export function ArmVideo({ videoRef }: ArmVideoProps) {
  return <video ref={videoRef} autoPlay playsInline muted />
}
