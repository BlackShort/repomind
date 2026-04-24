"use client"

import { useState } from 'react'
import { File, FileCode2, FileJson, FileText, Folder, FolderOpen, ImageIcon } from 'lucide-react'
import type { FileTree } from './types'

type TreeNodeProps = {
  name: string
  node: FileTree | 'file'
  depth?: number
}

function getFileIcon(fileName: string) {
  const ext = fileName.split('.').pop()?.toLowerCase() ?? ''

  if (["png", "jpg", "jpeg", "gif", "svg", "webp", "ico"].includes(ext)) {
    return <ImageIcon className="h-4 w-4 text-muted-foreground" />
  }

  if (["json", "yaml", "yml", "toml"].includes(ext)) {
    return <FileJson className="h-4 w-4 text-primary/80" />
  }

  if (["js", "jsx", "ts", "tsx", "py", "java", "go", "rb", "rs", "php", "c", "cpp"].includes(ext)) {
    return <FileCode2 className="h-4 w-4 text-primary" />
  }

  if (["md", "txt", "rst"].includes(ext)) {
    return <FileText className="h-4 w-4 text-muted-foreground" />
  }

  return <File className="h-4 w-4 text-muted-foreground" />
}

export default function TreeNode({ name, node, depth = 0 }: TreeNodeProps) {
  const [open, setOpen] = useState(depth < 1)
  const isFile = node === 'file'

  if (isFile) {
    return (
      <div className="group flex items-center gap-1.5 rounded-md py-1 pl-2 pr-1 hover:bg-accent/60">
        {getFileIcon(name)}
        <span className="mono truncate text-[11px] text-muted-foreground group-hover:text-foreground">{name}</span>
      </div>
    )
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full cursor-pointer items-center gap-1.5 rounded-md py-1 pl-2 pr-1 text-left transition-colors hover:bg-accent"
      >
        <span className="text-[10px] text-primary">{open ? '▾' : '▸'}</span>
        {open ? <FolderOpen className="h-4 w-4 text-primary" /> : <Folder className="h-4 w-4 text-primary/90" />}
        <span className="mono truncate text-[11px] text-primary">{name}</span>
      </button>
      {open && (
        <div className="ml-3 border-l border-border/60 pl-2">
          {Object.entries(node as FileTree).map(([k, v]) => (
            <TreeNode key={k} name={k} node={v} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  )
}
