import {
  Controls,
  FullscreenButton,
  LiveButton,
  MediaPlayer,
  MediaProvider,
  MuteButton,
  PIPButton,
  PlayButton,
} from '@vidstack/react'
import {
  MaximizeIcon,
  MinimizeIcon,
  PauseIcon,
  PictureInPicture2Icon,
  PictureInPictureIcon,
  PlayIcon,
  VideoIcon,
  Volume2Icon,
  VolumeXIcon,
} from 'lucide-react'
import type { MouseEvent } from 'react'

import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'

import type { TargetCommand } from './types'
import { framePixelFromClick } from './videoPixels'

import '@vidstack/react/player/styles/base.css'

type ArmVideoProps = {
  stream: MediaStream | null
  onTarget: (target: TargetCommand) => void
}

const controlButtonClassName =
  'inline-flex size-9 items-center justify-center rounded-lg text-primary-foreground outline-none hover:bg-primary-foreground/10 data-focus:ring-2 data-focus:ring-ring'

const playerSurfaceClassName = 'h-full w-full overflow-hidden bg-background'

export function ArmVideo({ stream, onTarget }: ArmVideoProps) {
  if (stream == null) {
    return (
      <div className="player-stage">
        <div className="player-frame">
          <Empty className={`${playerSurfaceClassName} rounded-none border-0`}>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <VideoIcon />
              </EmptyMedia>
              <EmptyTitle>Waiting for camera</EmptyTitle>
              <EmptyDescription>
                The arm feed will appear here once the signaling server connects.
              </EmptyDescription>
            </EmptyHeader>
          </Empty>
        </div>
      </div>
    )
  }

  function handleClick(event: MouseEvent<HTMLButtonElement>) {
    const video = event.currentTarget.parentElement?.querySelector('video')
    if (!(video instanceof HTMLVideoElement)) {
      return
    }
    const pixel = framePixelFromClick(event.clientX, event.clientY, video)
    if (pixel == null) {
      return
    }
    onTarget(pixel)
  }

  return (
    <div className="player-stage">
      <div className="player-frame">
        <MediaPlayer
          className={`${playerSurfaceClassName} font-sans text-primary-foreground [&_video]:h-full [&_video]:w-full [&_video]:object-contain`}
          src={{ src: stream, type: 'video/object' }}
          viewType="video"
          streamType="ll-live"
          title="Arm camera"
          load="eager"
          autoPlay
          muted
          playsInline
        >
          <MediaProvider />
          <button
            type="button"
            className="absolute inset-0 z-10 cursor-crosshair bg-transparent"
            aria-label="Set arm target"
            onClick={handleClick}
          />
          <div className="pointer-events-none absolute inset-0 bg-linear-to-t from-background/80 via-transparent to-background/30 opacity-0 transition-opacity media-paused:opacity-100 media-controls:opacity-100" />
          <Controls.Root className="pointer-events-none absolute inset-0 z-20 flex flex-col justify-between opacity-0 transition-opacity media-paused:opacity-100 media-controls:opacity-100">
            <Controls.Group className="flex items-center justify-between gap-3 p-3">
              <LiveButton className="pointer-events-auto rounded-md bg-destructive px-2 py-1 text-xs font-medium tracking-wide text-primary-foreground uppercase data-[ended]:hidden data-[live]:opacity-100 data-[edge]:opacity-100">
                Live
              </LiveButton>
            </Controls.Group>
            <Controls.Group className="flex items-center gap-1 p-3">
              <PlayButton className={`pointer-events-auto ${controlButtonClassName}`}>
                <PlayIcon className="hidden media-paused:block" />
                <PauseIcon className="media-paused:hidden" />
              </PlayButton>
              <MuteButton className={`pointer-events-auto ${controlButtonClassName}`}>
                <VolumeXIcon className="hidden media-muted:block" />
                <Volume2Icon className="media-muted:hidden" />
              </MuteButton>
              <div className="flex-1" />
              <PIPButton className={`pointer-events-auto ${controlButtonClassName}`}>
                <PictureInPicture2Icon className="media-pip:hidden" />
                <PictureInPictureIcon className="hidden media-pip:block" />
              </PIPButton>
              <FullscreenButton className={`pointer-events-auto ${controlButtonClassName}`}>
                <MaximizeIcon className="media-fullscreen:hidden" />
                <MinimizeIcon className="hidden media-fullscreen:block" />
              </FullscreenButton>
            </Controls.Group>
          </Controls.Root>
        </MediaPlayer>
      </div>
    </div>
  )
}
