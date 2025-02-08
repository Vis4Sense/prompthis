import { nextTick } from 'vue'
import { acceptHMRUpdate, defineStore } from 'pinia'

import { useStore as useSessionStore } from './session'

export interface Selector {
    field: string
    value: string
    triggerView: string
}

export const useStore = defineStore('controls', {
    state: () => ({
        showIVG: true, // whether to show image variant graph
        embeddingWeight: 0.5, // the weight of image embedding when mixing image and text
        minSimilarity: 0.6, // min prompt similarity for filtering prompt pairs
        edgeWeightMax: 1 as number, // max edge weight
        edgeWeightThresh: 0.5 as number, // threshold for edge weight
        clusterThresh: 0.5, // threshold for clustering
        promptPairs: [] as [number, number][], // pairs of prompts that are compared to derive edges, [prompt index, prompt index]
        stages: [] as number[][], // stages of the exploration
        fullImageModal: false, // whether to open full image
        fullImageData: null as string | null, // full image data,
        copiedPrompt: null as string | null, // copied prompt
        /** controls for interaction */
        hovered: null as Selector | null, // hovered
        selected: [] as Selector[], // selected
    }),
    getters: {
    },
    actions: {
        toggleIVG() {
            this.showIVG = !this.showIVG
        },
        setEmbeddingWeight(weight: number) {
            this.embeddingWeight = weight
        },
        setEdgeWeightMax(max: number) {
            this.edgeWeightMax = max
        },
        setEdgeWeightThresh(thresh: number) {
            this.edgeWeightThresh = thresh
        },
        setMinSimilarity(sim: number) {
            this.minSimilarity = sim
        },
        setClusterThresh(thresh: number) {
            this.clusterThresh = thresh
        },
        filterPromptPairs(simMtr: number[][]) {
            const n = simMtr.length
            const pairs = [] as [number, number][]
            for (let i = 0; i < n; i++) {
                for (let j = i + 1; j < n; j++) {
                    const sim = simMtr[i][j]
                    if (sim > this.minSimilarity) {
                        pairs.push([i, j])
                    }
                }
            }
            this.promptPairs = pairs
        },
        updateStages(simMtr: number[][]) {
            const n = simMtr.length
            const stages = [...this.stages]
            const steps = stages.flat()

            // if n - #steps = 1, add the last step and not change the stages
            if (steps.length > 0 && n - steps.length === 1) {
                if (simMtr[n-2][n-1] > this.minSimilarity) {
                    stages[stages.length - 1].push(n - 1)
                } else {
                    stages.push([n - 1])
                }
                this.stages = stages
                return
            }

            // otherwise, recalculate the stages
            stages.length = 0
            steps.length = 0

            // if there are new records, add them to the stages
            const preStep = steps.length ? steps[steps.length - 1] : -1
            const curStep = preStep + 1
            for (let step = curStep; step < n; step++) {
                if (stages.length === 0) {
                    stages.push([0])
                } else if (simMtr[step - 1][step] > this.minSimilarity) {
                    stages[stages.length - 1].push(step)
                } else {
                    stages.push([step])
                }
            }
            this.stages = stages
        },
        segmentStages(seg: number) {
            console.log('segment stages', seg)
            const stages = [...this.stages]

            // if seg is the beginning of a stage, merge it with the previous stage
            const begins = stages.map((stage) => stage[0])
            if (begins.includes(seg)) {
                const idx = begins.indexOf(seg)
                if (idx > 0) {
                    stages[idx - 1] = stages[idx - 1].concat(stages[idx])
                    stages.splice(idx, 1)
                }
            }

            // otherwise, split the stage
            else {
                const stageIdx = stages.findIndex((stage) => stage.includes(seg))
                const stage = stages[stageIdx]
                const idx = stage.indexOf(seg)
                // split the stage at idx
                const stage1 = stage.slice(0, idx)
                const stage2 = stage.slice(idx)
                stages[stageIdx] = stage1
                stages.splice(stageIdx + 1, 0, stage2)
            }

            this.stages = stages
        },
        emptyPromptPairs() {
            this.promptPairs = []
        },
        emptyStages() {
            this.stages = []
        },
        async openFullImage({data, filename}: {data: string, filename: string}) {
            this.fullImageModal = true
            this.fullImageData = data

            if (filename !== '') {
                const sessionStore = useSessionStore()
                const callback = (d: string) => {
                    this.fullImageData = d
                }
                sessionStore.fetchFullImage(filename, callback)
            }
        },
        setCopiedPrompt(prompt: string) {
            this.copiedPrompt = prompt
            nextTick(() => {
                this.copiedPrompt = null
            })
        },
        setHovered(selector: Selector | null = null) {
            console.log('set hovered', selector)
            this.hovered = selector
        },
        setSelected(selector: Selector | null = null) {
            console.log('set selected', selector)
            if (selector === null) {
                this.selected = []
            } else {
                this.selected = [selector]
            }
        },
        closeFullImage() {
            this.fullImageModal = false
            this.fullImageData = null
        }
    }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}