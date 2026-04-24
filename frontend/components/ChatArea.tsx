"use client"

import type { RefObject } from 'react'
import { Bot, MessageSquareQuote, SendHorizontal, Sparkles, UserCircle2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import type { Message } from './types'

const SUGGESTIONS = [
  'What does this project do?',
  'How is authentication handled?',
  'What is the folder structure?',
  'Where is the API layer?',
]

type ChatAreaProps = {
  messages: Message[]
  loading: boolean
  input: string
  sessionId: string
  bottomRef: RefObject<HTMLDivElement | null>
  setInput: (value: string) => void
  onQuery: () => void
}

export default function ChatArea({
  messages,
  loading,
  input,
  sessionId,
  bottomRef,
  setInput,
  onQuery,
}: ChatAreaProps) {
  return (
    <main className="flex min-w-0 flex-1 flex-col overflow-hidden">
      <div className="relative z-10 flex-1 overflow-y-auto bg-linear-to-b from-background via-background to-muted/20 px-6 py-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center gap-3.5">
            <div className="rounded-2xl border border-border bg-card p-3 shadow-sm">
              <Sparkles className="h-8 w-8 text-primary" />
            </div>
            <div className="text-[26px] font-extrabold tracking-tight">Ask your codebase</div>
            <div className="mono text-center text-[12px] leading-[1.7] text-muted-foreground">
              Paste a GitHub URL above and hit analyze.<br />Then ask anything about the code.
            </div>
            <div className="mt-1 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map(q => (
                <button
                  key={q}
                  type="button"
                  onClick={() => setInput(q)}
                  className="mono cursor-pointer rounded-full border border-input bg-card px-3.5 py-1.5 text-[11px] text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`msg-appear mb-4.5 flex gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div
              className={`mono flex h-6.5 w-6.5 shrink-0 items-center justify-center rounded-md border text-[11px] ${
                msg.role === 'user'
                  ? 'border-primary/40 bg-primary/10 text-primary'
                  : 'border-border bg-muted text-muted-foreground'
              }`}
            >
              {msg.role === 'user' ? <UserCircle2 className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>

            <div className="max-w-[76%]">
              <div
                className={`rounded-lg border px-3.5 py-2.5 text-[13px] leading-[1.75] text-foreground ${
                  msg.role === 'user'
                    ? 'border-primary/40 bg-primary/10 shadow-[0_6px_18px_-14px_hsl(var(--primary))]'
                    : 'border-border bg-muted shadow-sm'
                }`}
              >
                <ReactMarkdown
                  components={{
                    code: ({ children }) => (
                      <code className="mono rounded border border-border bg-background px-1.25 py-px text-[11px] text-primary">
                        {children}
                      </code>
                    ),
                    pre: ({ children }) => (
                      <pre className="mono mt-2 overflow-x-auto rounded-md border border-border bg-background px-3 py-2.5 text-[11px] leading-[1.6] text-primary">
                        {children}
                      </pre>
                    ),
                    p: ({ children }) => <p className="mb-1.5">{children}</p>,
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1.25">
                  {msg.sources.map(s => (
                    <span
                      key={s}
                      className="mono rounded border border-input bg-card px-1.75 py-0.5 text-[10px] text-muted-foreground"
                    >
                      {s.replace(/\\/g, '/')}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg-appear mb-4.5 flex gap-2.5">
            <div className="mono flex h-6.5 w-6.5 items-center justify-center rounded-md border border-border bg-muted text-[11px] text-muted-foreground">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-1.5 rounded-lg border border-border bg-muted px-3.5 py-2.5">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className={`h-1.5 w-1.5 rounded-full bg-primary ${
                    i === 0
                      ? 'animate-[pulse_1.2s_ease-in-out_0s_infinite]'
                      : i === 1
                        ? 'animate-[pulse_1.2s_ease-in-out_0.2s_infinite]'
                        : 'animate-[pulse_1.2s_ease-in-out_0.4s_infinite]'
                  }`}
                />
              ))}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="flex items-center gap-2.5 border-t border-border bg-card px-5 py-3">
        <span className="mono rounded-md border border-border bg-muted p-1 text-[16px] leading-none text-primary">
          <MessageSquareQuote className="h-3.5 w-3.5" />
        </span>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              onQuery()
            }
          }}
          placeholder={sessionId ? 'Ask about the codebase...' : 'Analyze a repo first'}
          disabled={!sessionId || loading}
          className="mono min-w-0 flex-1 border-none bg-transparent text-[13px] text-foreground outline-none disabled:opacity-35"
        />
        <button
          type="button"
          onClick={onQuery}
          disabled={!sessionId || !input.trim() || loading}
          className="mono inline-flex shrink-0 items-center gap-1 rounded-md bg-primary px-3.25 py-1.75 text-[12px] font-semibold text-primary-foreground transition-opacity disabled:cursor-not-allowed disabled:opacity-25"
        >
          <SendHorizontal className="h-3.5 w-3.5" />
          send
        </button>
      </div>
    </main>
  )
}
