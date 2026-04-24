"use client"

import { CheckCircle2, Link2, SearchCode, TriangleAlert } from 'lucide-react'

type HeaderBarProps = {
  url: string
  ingesting: boolean
  status: string
  error: string
  onUrlChange: (value: string) => void
  onIngest: () => void
}

export default function HeaderBar({
  url,
  ingesting,
  status,
  error,
  onUrlChange,
  onIngest,
}: HeaderBarProps) {
  return (
    <header className="flex shrink-0 items-center justify-between gap-3 border-b border-border bg-card/95 px-5 py-2.5 backdrop-blur">
      <div className="flex font-semibold tracking-wider text-xl font-mono">
        <span className='text-green-500'>repo</span>
        <span className='text-foreground'>Mind</span>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative min-w-sm max-w-lg w-full">
          <Link2 className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={url}
            onChange={e => onUrlChange(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && onIngest()}
            placeholder="https://github.com/owner/repo"
            className="mono min-w-0 w-full rounded-md border border-input bg-background px-8 py-1.75 text-[12px] text-foreground outline-none transition-colors focus-visible:border-primary"
          />
        </div>

        <button
          type="button"
          onClick={onIngest}
          disabled={ingesting || !url.trim()}
          className={`mono inline-flex shrink-0 items-center gap-1.5 rounded-md px-3.5 py-1.75 text-[12px] font-semibold text-primary-foreground disabled:cursor-not-allowed ${ingesting ? 'bg-primary/70' : 'bg-primary'
            }`}
        >
          <SearchCode className="h-4 w-4" />
          {ingesting ? 'indexing...' : 'analyze →'}
        </button>

        {status && !error && (
          <span className="mono inline-flex shrink-0 items-center gap-1 text-[11px] text-primary"><CheckCircle2 className="h-4 w-4" /> {status}</span>
        )}
        {error && (
          <span className="mono inline-flex max-w-55 shrink-0 items-center gap-1 truncate whitespace-nowrap text-[11px] text-destructive">
            <TriangleAlert className="h-4 w-4" /> {error}
          </span>
        )}
      </div>
    </header>
  )
}
