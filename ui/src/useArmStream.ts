import { useEffect, useRef, useState } from 'react'

import type { SolverResults, TargetCommand } from './types'

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const SIGNALING_URL = `${protocol}//${window.location.host}/ws`

export function useArmStream() {
  const socketRef = useRef<WebSocket | null>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [solver, setSolver] = useState<SolverResults | null>(null)

  useEffect(() => {
    let cancelled = false
    const pc = new RTCPeerConnection()
    const ws = new WebSocket(SIGNALING_URL)
    socketRef.current = ws
    pc.addTransceiver('video', { direction: 'recvonly' })
    pc.ontrack = (event) => {
      if (cancelled) {
        return
      }
      setStream(event.streams[0] ?? new MediaStream([event.track]))
    }
    pc.onicecandidate = (event) => {
      if (event.candidate == null || ws.readyState !== WebSocket.OPEN) {
        return
      }
      ws.send(JSON.stringify({ type: 'ice', candidate: event.candidate }))
    }

    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data) as { type: string } & SolverResults & {
        sdp: string
      }
      if (cancelled) {
        return
      }
      if (message.type === 'solver') {
        setSolver({
          success: message.success,
          solution: message.solution,
          reason: message.reason,
          runtime: message.runtime,
          target: message.target ?? null,
        })
        return
      }
      if (message.type !== 'offer') {
        return
      }
      await pc.setRemoteDescription({ type: 'offer', sdp: message.sdp })
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      if (cancelled || ws.readyState !== WebSocket.OPEN) {
        return
      }
      ws.send(JSON.stringify({ type: 'answer', sdp: pc.localDescription?.sdp }))
    }

    return () => {
      cancelled = true
      socketRef.current = null
      setStream(null)
      ws.close()
      void pc.close()
    }
  }, [])

  function sendTarget(target: TargetCommand) {
    const ws = socketRef.current
    if (ws == null || ws.readyState !== WebSocket.OPEN) {
      return
    }
    ws.send(JSON.stringify({ type: 'target', ...target }))
  }

  return { stream, solver, sendTarget }
}
