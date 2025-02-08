export interface T2IRecord {
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
    promptTokens: string[]
}

interface Point {
    x: number
    y: number
}

export interface WordChange {
    action: string
    word: string
    weight?: number
    frequency?: number
    included?: boolean
    display?: boolean
}

export interface Node {
    id: string
    promptId: number
    x: number
    y: number
    data: string
    width: number
    height: number
}

export interface Edge {
    id: number
    action: string
    changes: WordChange[]
    ratio: number
    src:  number
    src_clu: number
    src_pmt: number
    tgt: number
    tgt_clu: number
    tgt_pmt: number
    weight: number
    word: string
    display?: boolean
}

export interface EdgeGroup {
    idx: number
    action: string
    changes: WordChange[]
    src_clu: number
    tgt_clu: number
    weight: number
    word: string
    edges: number[]
    baryCenter: Point
}

export interface Selector {
    field: string
    value: object
    triggerView: string
}

interface ImageSelectorValue {
    imageId: string
    imageIndex: number
    promptIndex: number
}

export interface ImageSelector extends Selector {
    value: ImageSelectorValue
}

export interface WordSelectorValue {
    action: string
    text: string
}

export interface WordSelector extends Selector {
    value: WordSelectorValue
}

export interface PromptSelector extends Selector {
    value: number
}
