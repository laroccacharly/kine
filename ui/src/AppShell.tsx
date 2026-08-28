import type { ReactNode } from 'react'
import { useEffect, useRef, useState } from 'react'
import { BookOpenIcon, MenuIcon, Move3dIcon, RadioIcon, XIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export type AppPage = 'live' | 'motion'

export function AppShell({
  page,
  onPageChange,
  sidebar,
  children,
}: {
  page: AppPage
  onPageChange: (page: AppPage) => void
  sidebar: ReactNode
  children: ReactNode
}) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const menuButtonRef = useRef<HTMLButtonElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)

  function closeMobileSidebar() {
    setMobileOpen(false)
    requestAnimationFrame(() => menuButtonRef.current?.focus())
  }

  function navigate(nextPage: AppPage) {
    onPageChange(nextPage)
    closeMobileSidebar()
  }

  useEffect(() => {
    if (!mobileOpen) {
      return
    }
    closeButtonRef.current?.focus()
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        closeMobileSidebar()
      }
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [mobileOpen])

  return (
    <div className="flex h-svh overflow-hidden bg-background">
      <a
        href="#main-content"
        className="fixed left-3 top-3 z-[60] -translate-y-20 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground shadow-md transition-transform focus-visible:translate-y-0"
      >
        Skip to content
      </a>
      {mobileOpen ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/30 backdrop-blur-xs md:hidden"
          aria-label="Close controls"
          onClick={closeMobileSidebar}
        />
      ) : null}
      <aside
        id="controls-sidebar"
        aria-label="Arm controls"
        className={cn(
          'z-50 h-svh shrink-0 flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground',
          mobileOpen
            ? 'fixed inset-y-0 left-0 flex w-72 max-w-[85vw] shadow-xl md:static md:w-60 md:max-w-none md:shadow-none'
            : 'hidden w-60 md:flex',
        )}
      >
        <div className="flex h-16 items-center gap-3 border-b border-sidebar-border px-4">
          <div className="flex size-9 items-center justify-center rounded-lg border bg-background shadow-xs">
            <Move3dIcon className="size-4" aria-hidden="true" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-semibold">Kine</p>
            <p className="text-xs text-muted-foreground">Inverse kinematics</p>
          </div>
          <Button
            ref={closeButtonRef}
            type="button"
            variant="ghost"
            size="icon"
            className="text-sidebar-foreground md:hidden"
            aria-label="Close controls"
            onClick={closeMobileSidebar}
          >
            <XIcon aria-hidden="true" />
          </Button>
        </div>
        <nav aria-label="Main navigation" className="grid gap-1 border-b p-3">
          <Button
            variant={page === 'live' ? 'secondary' : 'ghost'}
            className="justify-start"
            aria-current={page === 'live' ? 'page' : undefined}
            onClick={() => navigate('live')}
          >
            <RadioIcon />
            Live arm
          </Button>
          <Button
            variant={page === 'motion' ? 'secondary' : 'ghost'}
            className="justify-start"
            aria-current={page === 'motion' ? 'page' : undefined}
            onClick={() => navigate('motion')}
          >
            <BookOpenIcon />
            How motion works
          </Button>
        </nav>
        {page === 'live' ? (
          <div className="flex-1 overflow-y-auto py-3">{sidebar}</div>
        ) : null}
      </aside>

      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-40 flex h-12 shrink-0 items-center gap-3 border-b bg-background/80 px-3 backdrop-blur-xl sm:px-5">
          <Button
            ref={menuButtonRef}
            type="button"
            variant="ghost"
            size="icon"
            className="md:hidden"
            aria-label="Open controls"
            aria-controls="controls-sidebar"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen(true)}
          >
            <MenuIcon aria-hidden="true" />
          </Button>
          <p className="min-w-0 flex-1 truncate text-sm font-medium">
            {page === 'live' ? 'Live' : 'How motion works'}
          </p>
        </header>
        <main
          id="main-content"
          className="flex min-h-0 flex-1 flex-col bg-muted/20 p-3 sm:p-4"
        >
          {children}
        </main>
      </div>
    </div>
  )
}
