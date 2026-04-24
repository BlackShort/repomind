"use client"

import TreeNode from './TreeNode'
import type { FileTree } from './types'

type FileExplorerProps = {
  fileTree: FileTree | null
}

export default function FileExplorer({ fileTree }: FileExplorerProps) {
  return (
    <aside
      className={`shrink-0 overflow-x-hidden scrollbar-thin overflow-y-auto border-r border-border bg-card/90 backdrop-blur transition-[width] duration-250 ease-in-out ${
        fileTree ? 'w-64' : 'w-0 border-r-0'
      }`}
    >
      {fileTree && (
        <div className="min-w-64 py-3 px-1.5">
          {Object.entries(fileTree).map(([k, v]) => (
            <TreeNode key={k} name={k} node={v} depth={0} />
          ))}
        </div>
      )}
    </aside>
  )
}
