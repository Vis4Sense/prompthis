import { CamelCaseList } from '../utils/namestyle'

interface RawSessionItem {
    sessionId: number
    sessionName: string
    createTime: string
    createTimeZone: string
    updateTime: string
    updateTimeZone: string
}

export interface SessionItem extends RawSessionItem { }

interface RawRecord {
    promptId: number
    model: string
    createTime: string
    createTimezone: string
    finishTime: string
    finishTimezone: string
    width: number
    height: number
    steps: number
    batchSize: number
    prompt: string
    negativePrompt?: string
    settingFilename: string
    outputFilenames: string[]
    ratings?: number[]
}

export interface T2IRecord extends RawRecord {
    promptTokens: string[]
    promptTokenDiff: DiffWord[]
    showDiff: boolean
}

export interface CacheRecord {
    promptId?: number
    prompt: string
    images?: Record<string, string>
    projection?: Record<string, Point>
}

export interface Point {
    x: number,
    y: number
}

export interface RawSessionData {
    records: object[],
    images: Record<string, string>,
    image_projection: Record<string, [number, number]>
    text_projection: Record<string, [number, number]>
}

interface SessionData {
    records: T2IRecord[]
    images: Record<string, string>
    image_projection: Record<string, Point>
    text_projection: Record<string, Point>
}

// word-level comparison result
interface DiffWord {
    id: string
    text: string
    label: string
    action: string
    pre_weight: number
    cur_weight: number
    prev: object[]
    next: object[]
    weight: number
}
interface DiffPrompt {
    id: string
    text: string
    words: DiffWord[]
}

// word change
interface WordChange {
    action: string
    word: string
}

export interface WordEdge {
    action: string
    changes: WordChange[]
    ratio: number
    src: string
    src_clu: number
    src_pmt: number
    tgt: string
    tgt_clu: number
    tgt_pmt: number
    weight: number
    word: string
}

export interface RawEdgeGroup {
    action: string
    changes: WordChange[]
    src_clu: number
    tgt_clu: number
    weight: number
    word: string
}

export interface EdgeGroup extends RawEdgeGroup {
    idx: number
    edges: number[]
}

export const transformRawSessionList = (data: RawSessionItem[]): SessionItem[] => {
    return CamelCaseList(data) as SessionItem[]
}

export const transformRawSessionData = (data: RawSessionData): SessionData => {
    console.log('transform raw session data')
    console.log(data)
    const records = CamelCaseList(data.records) as T2IRecord[]
    const images = data.images
    const image_projection = Object.fromEntries(
        Object
            .entries(data.image_projection)
            .map(([key, value]) => [key, { x: value[0], y: value[1] } as Point])
    ) as Record<string, Point>
    const text_projection = Object.fromEntries(
        Object
            .entries(data.text_projection)
            .map(([key, value]) => [key, { x: value[0], y: value[1] } as Point])
    ) as Record<string, Point>

    return {
        records: records,
        images: images,
        image_projection: image_projection,
        text_projection: text_projection
    }
}

export const addTokenToRecords = (records: T2IRecord[], prompts: object[]) => {
    const prompts_ = prompts as DiffPrompt[]
    const records_ = records.map((record, index) => {
        const prompt = prompts_[index]
        const tokens = prompt.words.filter(word => word.action !== 'r').map((word) => word.text)
        return { ...record, promptTokens: tokens, promptTokenDiff: prompt.words }
    })
    return records_
}
