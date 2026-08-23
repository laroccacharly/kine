import { useEffect, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Field, FieldGroup, FieldLabel, FieldLegend, FieldSet } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'

import type { JointMotionConfig, TipPosition, WorldTarget } from './types'

const DEFAULT_X = 2
const DEFAULT_Y = 0

type ConfigFormProps = {
  target: TipPosition | null
  motion: JointMotionConfig | null
  onUpdateTarget: (target: WorldTarget) => void
  onUpdateMotionConfig: (motion: JointMotionConfig) => void
  isTargetPending: boolean
  isMotionConfigPending: boolean
}

function parseFinite(value: string): number | null {
  if (value.trim() === '') {
    return null
  }
  const parsed = Number(value)
  if (!Number.isFinite(parsed)) {
    return null
  }
  return parsed
}

function parsePositive(value: string): number | null {
  const parsed = parseFinite(value)
  if (parsed == null || parsed <= 0) {
    return null
  }
  return parsed
}

export function ConfigForm({
  target,
  motion,
  onUpdateTarget,
  onUpdateMotionConfig,
  isTargetPending,
  isMotionConfigPending,
}: ConfigFormProps) {
  const [x, setX] = useState(String(DEFAULT_X))
  const [y, setY] = useState(String(DEFAULT_Y))
  const [maxSpeed, setMaxSpeed] = useState('')
  const [accel, setAccel] = useState('')
  const [settle, setSettle] = useState('')

  useEffect(() => {
    if (target == null) {
      return
    }
    setX(String(target.x))
    setY(String(target.y))
  }, [target])

  useEffect(() => {
    if (motion == null) {
      return
    }
    setMaxSpeed(String(motion.max_speed_rad_s))
    setAccel(String(motion.acceleration_rad_s2))
    setSettle(String(motion.settle_rad))
  }, [motion])

  return (
    <div className="flex flex-col gap-6 px-4">
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault()
          const parsedX = parseFinite(x)
          const parsedY = parseFinite(y)
          if (parsedX == null || parsedY == null) {
            return
          }
          onUpdateTarget({ x: parsedX, y: parsedY })
        }}
      >
        <FieldSet>
          <FieldLegend variant="label">World target</FieldLegend>
          <FieldGroup className="grid grid-cols-2 gap-3">
            <Field>
              <FieldLabel htmlFor="target-x">X (m)</FieldLabel>
              <Input
                id="target-x"
                type="number"
                step="0.1"
                required
                className="font-mono tabular-nums"
                value={x}
                onChange={(event) => setX(event.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="target-y">Y (m)</FieldLabel>
              <Input
                id="target-y"
                type="number"
                step="0.1"
                required
                className="font-mono tabular-nums"
                value={y}
                onChange={(event) => setY(event.target.value)}
              />
            </Field>
          </FieldGroup>
        </FieldSet>
        <Button type="submit" className="w-full" disabled={isTargetPending}>
          {isTargetPending ? 'Updating target…' : 'Update target'}
        </Button>
      </form>
      <Separator />
      <form
        className="flex flex-col gap-4"
        onSubmit={(event) => {
          event.preventDefault()
          const max_speed_rad_s = parsePositive(maxSpeed)
          const acceleration_rad_s2 = parsePositive(accel)
          const settle_rad = parsePositive(settle)
          if (
            max_speed_rad_s == null ||
            acceleration_rad_s2 == null ||
            settle_rad == null
          ) {
            return
          }
          onUpdateMotionConfig({ max_speed_rad_s, acceleration_rad_s2, settle_rad })
        }}
      >
        <FieldSet>
          <FieldLegend variant="label">Motion config</FieldLegend>
          <FieldGroup className="gap-3">
            <Field>
              <FieldLabel htmlFor="motion-max-speed">Max speed (rad/s)</FieldLabel>
              <Input
                id="motion-max-speed"
                type="number"
                min="0"
                step="0.05"
                required
                className="font-mono tabular-nums"
                value={maxSpeed}
                onChange={(event) => setMaxSpeed(event.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="motion-accel">Acceleration (rad/s²)</FieldLabel>
              <Input
                id="motion-accel"
                type="number"
                min="0"
                step="0.05"
                required
                className="font-mono tabular-nums"
                value={accel}
                onChange={(event) => setAccel(event.target.value)}
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="motion-settle">Settle threshold (rad)</FieldLabel>
              <Input
                id="motion-settle"
                type="number"
                min="0"
                step="0.0001"
                required
                className="font-mono tabular-nums"
                value={settle}
                onChange={(event) => setSettle(event.target.value)}
              />
            </Field>
          </FieldGroup>
        </FieldSet>
        <Button type="submit" className="w-full" disabled={isMotionConfigPending}>
          {isMotionConfigPending ? 'Saving motion…' : 'Save motion settings'}
        </Button>
      </form>
    </div>
  )
}
