import { useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Field, FieldLabel } from '@/components/ui/field'
import { Input } from '@/components/ui/input'

import type { JointMotionConfig } from './types'

type MotionFormProps = {
  motion: JointMotionConfig | null
  onSubmit: (motion: JointMotionConfig) => void
}

function parsePositive(value: string): number | null {
  if (value.trim() === '') {
    return null
  }
  const parsed = Number(value)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return null
  }
  return parsed
}

export function MotionForm({ motion, onSubmit }: MotionFormProps) {
  const [maxSpeed, setMaxSpeed] = useState('')
  const [accel, setAccel] = useState('')
  const [settle, setSettle] = useState('')

  useEffect(() => {
    if (motion == null) {
      return
    }
    setMaxSpeed(String(motion.max_speed_rad_s))
    setAccel(String(motion.acceleration_rad_s2))
    setSettle(String(motion.settle_rad))
  }, [motion])

  return (
    <form
      className="flex flex-wrap items-end gap-3"
      onSubmit={(event) => {
        event.preventDefault()
        const max_speed_rad_s = parsePositive(maxSpeed)
        const acceleration_rad_s2 = parsePositive(accel)
        const settle_rad = parsePositive(settle)
        if (max_speed_rad_s == null || acceleration_rad_s2 == null || settle_rad == null) {
          return
        }
        onSubmit({ max_speed_rad_s, acceleration_rad_s2, settle_rad })
      }}
    >
      <Field orientation="horizontal" className="w-auto">
        <FieldLabel htmlFor="motion-max-speed">max speed</FieldLabel>
        <Input
          id="motion-max-speed"
          type="number"
          min="0"
          step="0.05"
          className="w-24"
          value={maxSpeed}
          onChange={(event) => setMaxSpeed(event.target.value)}
        />
      </Field>
      <Field orientation="horizontal" className="w-auto">
        <FieldLabel htmlFor="motion-accel">accel</FieldLabel>
        <Input
          id="motion-accel"
          type="number"
          min="0"
          step="0.05"
          className="w-24"
          value={accel}
          onChange={(event) => setAccel(event.target.value)}
        />
      </Field>
      <Field orientation="horizontal" className="w-auto">
        <FieldLabel htmlFor="motion-settle">settle</FieldLabel>
        <Input
          id="motion-settle"
          type="number"
          min="0"
          step="0.0001"
          className="w-24"
          value={settle}
          onChange={(event) => setSettle(event.target.value)}
        />
      </Field>
      <Button type="submit">Apply</Button>
    </form>
  )
}
