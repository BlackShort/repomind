export type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

export type FileTree = { [key: string]: FileTree | 'file' }
