"use client"

import { useState, useRef, useEffect } from 'react'
import HeaderBar from '../components/HeaderBar'
import FileExplorer from '../components/FileExplorer'
import ChatArea from '../components/ChatArea'
import type { FileTree, Message } from '../components/types'

const API = 'http://127.0.0.1:8000/api'

export default function Home() {
  const [url, setUrl] = useState('')
  const [sessionId, setSessionId] = useState('')
  const [fileTree, setFileTree] = useState<FileTree | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [ingesting, setIngesting] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleIngest() {
    if (!url.trim() || ingesting) return
    setIngesting(true)
    setError('')
    setStatus('cloning...')
    setFileTree(null)
    setMessages([])
    setSessionId('')

    try {
      const res = await fetch(`${API}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_url: url.trim() }),
      })
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Ingestion failed') }
      const data = await res.json()
      setSessionId(data.session_id)
      setFileTree(data.file_tree)
      setStatus(data.status === 'already_indexed'
        ? 'already indexed'
        : `${data.total_files} files · ${data.total_chunks} chunks`)
      setMessages([{
        role: 'assistant',
        content: `Codebase indexed. I've analyzed **${data.total_files ?? 'all'}** files across this repository. Ask me anything about the code.`,
      }])
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
      setStatus('')
    } finally {
      setIngesting(false)
    }
  }

  async function handleQuery() {
    if (!input.trim() || !sessionId || loading) return
    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const res = await fetch(`${API}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question }),
      })
      if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Query failed') }
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch (e: unknown) {
      setMessages(prev => [...prev, { role: 'assistant', content: `⚠ ${e instanceof Error ? e.message : 'Error'}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-background text-foreground">
      <HeaderBar
        url={url}
        ingesting={ingesting}
        status={status}
        error={error}
        onUrlChange={setUrl}
        onIngest={handleIngest}
      />

      <div className="relative flex flex-1 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_15%,hsl(var(--primary)/0.08),transparent_45%),radial-gradient(circle_at_80%_30%,hsl(var(--ring)/0.06),transparent_40%)]" />
        <FileExplorer fileTree={fileTree} />

        <ChatArea
          messages={messages}
          loading={loading}
          input={input}
          sessionId={sessionId}
          bottomRef={bottomRef}
          setInput={setInput}
          onQuery={handleQuery}
        />
      </div>
    </div>
  )
}