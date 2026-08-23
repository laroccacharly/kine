import { useEffect, useState } from 'react'

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const SIGNALING_URL = `${protocol}//${window.location.host}/ws/signaling`

type SignalingMessage = {
  type: 'offer'
  sdp: string
}

export function useArmVideo() {
  const [stream, setStream] = useState<MediaStream | null>(null)

  useEffect(() => {
    let cancelled = false
    const pc = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
    })
    const ws = new WebSocket(SIGNALING_URL)
    pc.addTransceiver('video', { direction: 'recvonly' })
    pc.ontrack = (event) => {
      if (!cancelled) {
        setStream(event.streams[0] ?? new MediaStream([event.track]))
      }
    }
    pc.onicecandidate = (event) => {
      if (event.candidate != null && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ice', candidate: event.candidate }))
      }
    }
    ws.onmessage = async (event) => {
      const message = JSON.parse(event.data) as SignalingMessage
      if (cancelled || message.type !== 'offer') {
        return
      }
      await pc.setRemoteDescription({ type: 'offer', sdp: message.sdp })
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      if (!cancelled && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'answer', sdp: pc.localDescription?.sdp }))
      }
    }

    return () => {
      cancelled = true
      setStream(null)
      ws.close()
      void pc.close()
    }
  }, [])

  return { stream }
}
