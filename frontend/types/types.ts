export type MessageRole = 'user' | 'assistant'

export interface Message {
    role: MessageRole
    content: string
    sources?: string[]
}

export type FileTree = {
    [key: string]: FileTree | 'file'
}

export interface IngestResponse {
    session_id: string
    status: 'indexed' | 'already_indexed'
    total_files?: number
    total_chunks?: number
    file_tree: FileTree
}

export interface QueryResponse {
    question: string
    answer: string
    sources: string[]
}

export interface ApiError {
    detail: string
}