import { useState } from 'react'

import { Button } from '@/components/ui/button'
import { Field, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'

import type { TargetCommand } from './types'

const DEFAULT_X = 2
const DEFAULT_Y = 0

type TargetFormProps = {
  onSubmit: (target: TargetCommand) => void
}

export function TargetForm({ onSubmit }: TargetFormProps) {
  const [x, setX] = useState(String(DEFAULT_X))
  const [y, setY] = useState(String(DEFAULT_Y))

  return (
    <form
      className="flex flex-wrap items-end gap-3"
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
        onSubmit({ x: parsedX, y: parsedY })
      }}
    >
      <Field orientation="horizontal" className="w-auto">
        <FieldLabel htmlFor="target-x">x</FieldLabel>
        <Input
          id="target-x"
          type="number"
          step="0.1"
          className="w-24"
          value={x}
          onChange={(event) => setX(event.target.value)}
        />
      </Field>
      <Field orientation="horizontal" className="w-auto">
        <FieldLabel htmlFor="target-y">y</FieldLabel>
        <Input
          id="target-y"
          type="number"
          step="0.1"
          className="w-24"
          value={y}
          onChange={(event) => setY(event.target.value)}
        />
      </Field>
      <Button type="submit">Update</Button>
    </form>
  )
}
