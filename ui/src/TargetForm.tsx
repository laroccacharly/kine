import { useState } from 'react'

const DEFAULT_X = 2
const DEFAULT_Y = 0

type TargetFormProps = {
  onSubmit: (x: number, y: number) => void
}

export function TargetForm({ onSubmit }: TargetFormProps) {
  const [x, setX] = useState(String(DEFAULT_X))
  const [y, setY] = useState(String(DEFAULT_Y))

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault()
        if (x.trim() === '' || y.trim() === '') {
          return
        }
        const parsedX = Number(x)
        const parsedY = Number(y)
        if (!Number.isFinite(parsedX) || !Number.isFinite(parsedY)) {
          return
        }
        onSubmit(parsedX, parsedY)
      }}
    >
      <label>
        x
        <input
          type="number"
          step="0.1"
          value={x}
          onChange={(event) => setX(event.target.value)}
        />
      </label>
      <label>
        y
        <input
          type="number"
          step="0.1"
          value={y}
          onChange={(event) => setY(event.target.value)}
        />
      </label>
      <button type="submit">Update</button>
    </form>
  )
}
