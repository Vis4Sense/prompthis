import type { RawEdgeGroup, WordEdge } from '@/plugins/session'

const url_host = 'https://vis.pku.edu.cn/prompthis'

const url_paths = {
    createSession: '/create/session',
    fetchSessionList: '/fetch/session_list',
    fetchSessionData: '/fetch/session_data',
    fetchNewData: '/fetch/new_data',
    fetchFullImage: '/fetch/full_image',
    logIn: '/login',
    runGeneration: '/generate',
    tokenizePrompts: '/prompt/tokenize',
    clusterImages: '/image/cluster',
    deriveEdges: '/compute/edge_derive',
}

export const urls = Object.fromEntries(
    Object
        .entries(url_paths)
        .map(([key, value]) => [key, url_host + value])
)

console.log(urls)

export interface FetchSessionRequest {
    userId?: number
    sessionId?: number
}

export interface BaseResponse {
    status: string
}

export interface LogInResponse extends BaseResponse {
    userId: number
}

export interface CreateSessionResponse extends BaseResponse {
    sessions: object[]
}

export interface GenerationResponse {
    status: string
    promptId: number | undefined
    message: string
}

export interface NewDataResponse {
    status: string
    data?: object
}

interface TokenizePromptsData {
    prompts: object[]
}

export interface TokenizePromptResponse {
    data: TokenizePromptsData
}

interface ImageClusterData {
    clusters: Record<string, number>
}

export interface ImageClusterResponse {
    data: ImageClusterData
}

interface EdgeDeriveData {
    edges: WordEdge[]
    edgeGroups: RawEdgeGroup[]
}

export interface EdgeDeriveResponse {
    data: EdgeDeriveData
}
