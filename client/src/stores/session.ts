import { acceptHMRUpdate, defineStore } from 'pinia'
import { useStore as useUserStore } from './user'

import { urls } from '../plugins/apis'
import { request, poll } from '../utils/request'
import { jacardSimilarity } from '../utils/similarity'

import type { RawSessionData, T2IRecord, CacheRecord, Point, WordEdge, EdgeGroup } from '../plugins/session'
import type { FetchSessionRequest, GenerationResponse, NewDataResponse, TokenizePromptResponse, ImageClusterResponse, EdgeDeriveResponse } from '../plugins/apis'
import { transformRawSessionData, addTokenToRecords } from '../plugins/session'

export const useStore = defineStore('session', {
    state: () => ({
        records: [] as T2IRecord[],
        images: {} as Record<string, string>,
        image_projection: {} as Record<string, Point>,
        text_projection: {} as Record<string, Point>,
        clusters: {} as Record<string, number>,
        cache: null as CacheRecord | null,
        edges: [] as WordEdge[],
        edgeGroups: [] as EdgeGroup[],
    }),
    getters: {
        promptSimilarityMatrix(state) {
            const { records } = state
            const n = records.length
            const matrix = Array(n).fill(0).map(() => Array(n).fill(0))
            for (let i = 0; i < n; i++) {
                const prompt_i = records[i].promptTokens
                for (let j = i + 1; j < n; j++) {
                    const prompt_j = records[j].promptTokens
                    matrix[i][j] = jacardSimilarity(prompt_i, prompt_j)
                }
            }
            return matrix
        }
    },
    actions: {
        async fetchSessionData() {
            const userStore = useUserStore()
            const payload = {} as FetchSessionRequest
            if (userStore.userId !== null && userStore.sessionId !== null) {
                payload['userId'] = userStore.userId
                payload['sessionId'] = userStore.sessionId
            }
            const data = await request<RawSessionData>(urls.fetchSessionData, payload)
            const { records, images, image_projection, text_projection } = transformRawSessionData(data)

            this.records = records
            this.images = images
            this.image_projection = image_projection
            this.text_projection = text_projection
        },
        async fetchFullImage(filename: string, callback: (d: string) => void) {
            const userStore = useUserStore()
            const { userId, sessionId } = userStore
            const payload = { userId, sessionId, filename }
            const data = await request<{data: string}>(urls.fetchFullImage, payload)
            callback(data.data)
            return data
        },
        async runGeneration(payload: CacheRecord) {
            const userStore = useUserStore()
            const { userId, sessionId } = userStore
            const data = await request<GenerationResponse>(urls.runGeneration, {
                ...payload, userId, sessionId
            })
            const { status, promptId, message } = data
            const { prompt } = payload
            if (status !== 'success') {
                return status
            }
            this.cache = { promptId, prompt }
            const action = () => request<NewDataResponse>(urls.fetchNewData, { promptId, userId, sessionId })
            const onSuccess = (result) => {
                const { records, images, image_projection, text_projection } = transformRawSessionData(result.data)
                this.image_projection = { ...this.image_projection, ...image_projection }
                this.text_projection = { ...this.text_projection, ...text_projection }
                this.images = { ...this.images, ...images }
                this.records = records
                this.emptyCache()
            }
            poll(action, onSuccess)
        },
        async tokenizePrompts() {
            const prompts = this.records.map((record) => ({ prompt: record.prompt }))
            const payload = { prompts }
            const data = await request<TokenizePromptResponse>(urls.tokenizePrompts, payload)
            const tokenizedPrompts = data.data.prompts
            const records = addTokenToRecords(this.records, tokenizedPrompts)
            this.records = records
        },
        async clusterImages(projection: Record<string, Point>, thresh: number) {
            const payload = { embeddings: projection, threshold: thresh }
            const data = await request<ImageClusterResponse>(urls.clusterImages, payload)
            this.clusters = data.data.clusters
        },
        async deriveEdges(promptPairs: [number, number][]) {
            // prompts
            const prompts = this.records.map((record) => ({ words:
                record.promptTokens.map((token) => ({ text: token, weight: 1 }))
            }))
            // image indexes
            const imageIndices = this.records.map((record) => (
                record.outputFilenames.map((filename) => (
                    filename.slice(0, filename.lastIndexOf('.'))
                ))
            ))
            const imageClusters = this.clusters
            const payload = { prompts, promptPairs, imageClusters, imageIndices }
            const data = await request<EdgeDeriveResponse>(urls.deriveEdges, payload)
            const { edges, edgeGroups } = data.data

            const edgeGroups_ = edgeGroups as EdgeGroup[]
            edgeGroups_.forEach((group, index) => {
                const subEdges = [] as number[]
                edges.forEach((edge, index) => {
                    if (
                        edge.word === group.word &&
                        edge.action === group.action &&
                        edge.src_clu === group.src_clu &&
                        edge.tgt_clu === group.tgt_clu
                    ) subEdges.push(index)
                })
                group.edges = subEdges
                group.idx = index
            })

            this.edges = edges
            this.edgeGroups = edgeGroups_
        },
        emptySessionData() {
            this.records = []
            this.images = {}
            this.image_projection = {}
            this.text_projection = {}
            this.clusters = {}
            this.cache = null
            this.edges = []
            this.edgeGroups = []
        },
        emptyCache() {
            this.cache = null
        }
    },
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}
