import {
  Controls,
  FullscreenButton,
  Gesture,
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

import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty'

import '@vidstack/react/player/styles/base.css'

type ArmVideoProps = {
  stream: MediaStream | null
}

const controlButtonClassName =
  'inline-flex size-9 items-center justify-center rounded-lg text-primary-foreground outline-none hover:bg-primary-foreground/10 data-focus:ring-2 data-focus:ring-ring'

export function ArmVideo({ stream }: ArmVideoProps) {
  if (stream == null) {
    return (
      <Empty className="h-full min-h-[28rem] rounded-none border-0 bg-background">
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
    )
  }

  return (
    <MediaPlayer
      className="h-full min-h-[28rem] w-full overflow-hidden bg-background font-sans text-primary-foreground"
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
      <Gesture className="absolute inset-0" event="pointerup" action="toggle:paused" />
      <div className="pointer-events-none absolute inset-0 bg-linear-to-t from-background/80 via-transparent to-background/30 opacity-0 transition-opacity media-paused:opacity-100 media-controls:opacity-100" />
      <Controls.Root className="absolute inset-0 flex flex-col justify-between opacity-0 transition-opacity media-paused:opacity-100 media-controls:opacity-100">
        <Controls.Group className="flex items-center justify-between gap-3 p-3">
          <LiveButton className="rounded-md bg-destructive px-2 py-1 text-xs font-medium tracking-wide text-primary-foreground uppercase data-[ended]:hidden data-[live]:opacity-100 data-[edge]:opacity-100">
            Live
          </LiveButton>
        </Controls.Group>
        <Controls.Group className="flex items-center gap-1 p-3">
          <PlayButton className={controlButtonClassName}>
            <PlayIcon className="hidden media-paused:block" />
            <PauseIcon className="media-paused:hidden" />
          </PlayButton>
          <MuteButton className={controlButtonClassName}>
            <VolumeXIcon className="hidden media-muted:block" />
            <Volume2Icon className="media-muted:hidden" />
          </MuteButton>
          <div className="flex-1" />
          <PIPButton className={controlButtonClassName}>
            <PictureInPicture2Icon className="media-pip:hidden" />
            <PictureInPictureIcon className="hidden media-pip:block" />
          </PIPButton>
          <FullscreenButton className={controlButtonClassName}>
            <MaximizeIcon className="media-fullscreen:hidden" />
            <MinimizeIcon className="hidden media-fullscreen:block" />
          </FullscreenButton>
        </Controls.Group>
      </Controls.Root>
    </MediaPlayer>
  )
}
