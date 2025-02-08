<script lang="ts" setup>
import { onMounted, ref, nextTick } from 'vue'
import { computed, watch } from 'vue'
import { useElementSize } from '@vueuse/core'

import { storeToRefs } from 'pinia'
import { useStore as useSessionStore } from '../stores/session'
import { useStore as useUserStore } from '../stores/user'
import { useStore as useControlStore } from '../stores/control'

import type { Point } from '@/plugins/session'

import VHistoryBox from './VHistoryBox.vue'
import VMiniMap from './VMiniMap.vue'
import VImageVariantGraph from './VImageVariantGraph/IVG.vue'

const miniMapContainer = ref<HTMLDivElement>()
const minimapSize = useElementSize(miniMapContainer)

const renderMiniMap = ref(false)

const ivgContainer = ref<HTMLDivElement>()
const ivgSize = useElementSize(ivgContainer)
const ivgWidth = computed(() => ivgSize.width.value)
const ivgHeight = computed(() => ivgSize.height.value)

const sessionStore = useSessionStore()
const userStore = useUserStore()
const controlStore = useControlStore()

const { sessionId } = storeToRefs(userStore)
const { records, images, image_projection, text_projection, clusters, edges, edgeGroups, cache } = storeToRefs(sessionStore)
const { embeddingWeight, minSimilarity, clusterThresh, showIVG, promptPairs, stages, edgeWeightThresh, hovered, selected } = storeToRefs(controlStore)
const similarityMatrix = computed(() => sessionStore.promptSimilarityMatrix)

// calculate input data of view components
const projection = computed(() => {
    const imageProjectionText = {} as Record<string, Point>
    const projection = {} as Record<string, Point>

    records.value.forEach((record) => {
        const outputFilenames = record.outputFilenames
        const settingFilename = record.settingFilename
        outputFilenames.forEach((filename) => {
            filename = filename.slice(0, filename.lastIndexOf('.'));
            imageProjectionText[filename] = text_projection.value[settingFilename]
        })
    })

    for (const [key, value] of Object.entries(image_projection.value)) {
        projection[key] = {
            x: embeddingWeight.value * value.x + (1 - embeddingWeight.value) * imageProjectionText[key].x,
            y: embeddingWeight.value * value.y + (1 - embeddingWeight.value) * imageProjectionText[key].y,
        }
    }

    return projection
})
const historyBoxRecords = computed(() => {
    console.log('recompute history box records')
    const completeRecords = records.value.map((d) => {
        return {
            meta: {...d, showDiff: false},
            details: d.outputFilenames.map((filename: string) => {
                const id = filename.slice(0, filename.lastIndexOf('.'))
                const image = images.value[filename]
                return { id, data: image }
            })
        }
    })
    promptPairs.value.forEach(([prompt1, prompt2]) => {
        if (prompt1 + 1 === prompt2) {
            completeRecords[prompt2].meta.showDiff = true
        }
    })
    if (cache.value) {
        return [...completeRecords, { meta: cache.value, details: [] }]
    } else {
        return completeRecords
    }
})

const handleEdgeWeightThreshChange = (value: number) => {
    controlStore.setEdgeWeightThresh(value)
}
const handleEdgeMaxWeightChange = (value: number) => {
    controlStore.setEdgeWeightMax(value)
}

const renderIvg = ref(true)

onMounted(() => {
    if (sessionId.value !== null) sessionStore.fetchSessionData()
})

watch(sessionId, () => {
    renderIvg.value = false
    sessionStore.emptyCache()
    controlStore.emptyPromptPairs()
    controlStore.emptyStages()
    sessionStore.emptySessionData()
    sessionStore.fetchSessionData()
    nextTick(() => {
        renderIvg.value = true
    })
})

watch(() => minimapSize, () => {
    if (minimapSize.width.value !== 0) {
        renderMiniMap.value = true
    }
}, { deep: true })


// actions after loading records or new record added
watch( records, async (newVal, oldVal) => {
    if (!records || records.value.length === 0) return
    // tokenize prompts when there is a new record
    if (newVal.length === oldVal.length) return
    controlStore.emptyPromptPairs()
    await sessionStore.tokenizePrompts()
    controlStore.filterPromptPairs(sessionStore.promptSimilarityMatrix)
    controlStore.updateStages(sessionStore.promptSimilarityMatrix)
    // cluster images
    await sessionStore.clusterImages(projection.value, clusterThresh.value)
    // derive edges
    sessionStore.deriveEdges(promptPairs.value)
}, { deep: false })

// filter prompt pairs
watch( minSimilarity, () => {
    controlStore.filterPromptPairs(sessionStore.promptSimilarityMatrix)
    controlStore.updateStages(sessionStore.promptSimilarityMatrix)
    sessionStore.deriveEdges(promptPairs.value)
})

// recalculate cluster when the distance threshold changes
watch( clusterThresh, async () => {
    await sessionStore.clusterImages(projection.value, clusterThresh.value)
    sessionStore.deriveEdges(promptPairs.value)
})

const emit = defineEmits(['open-image'])
</script>

<template>
    <div class="flex bg-white">
        <div class="w-50/85" ref="ivgContainer">
            <VImageVariantGraph
                v-if="showIVG && renderIvg"
                :records="records"
                :images="images"
                :projection="projection"
                :clusters="clusters"
                :edges="edges"
                :edge-groups="edgeGroups"
                :stages="stages"
                :canvas-width="ivgWidth"
                :canvas-height="ivgHeight"
                :min-edge-weight="edgeWeightThresh"
                :hovered="hovered"
                @update-weight-thresh="handleEdgeWeightThreshChange"
                @update-max-weight="handleEdgeMaxWeightChange"
                @hover-image="controlStore.setHovered({
                    field: 'image',
                    value: $event,
                    triggerView: 'ivg'
                })"
                @unhover-image="controlStore.setHovered(null)"
                @click-image="controlStore.setSelected({
                    field: 'image',
                    value: $event,
                    triggerView: 'ivg'
                })"
                @open-image="emit('open-image', $event)"
                @copy-prompt="controlStore.setCopiedPrompt($event)"
            />
        </div>
        <div class="flex w-35/85">
            <div class="flex-grow">
                <div class="h-full">
                    <VHistoryBox
                        :records="historyBoxRecords"
                        :cache="cache"
                        :hovered="hovered"
                        :selected="selected"
                        @open-image="emit('open-image', $event)"
                        @copy-prompt="controlStore.setCopiedPrompt($event)"
                        @hover-image="controlStore.setHovered({
                            field: 'image',
                            value: $event,
                            triggerView: 'historyBox'
                        })"
                        @unhover-image="controlStore.setHovered(null)"
                        @hover-word="controlStore.setHovered({
                            field: 'word',
                            value: $event,
                            triggerView: 'historyBox'
                        })"
                        @unhover-word="controlStore.setHovered(null)"
                        @hover-prompt="controlStore.setHovered({
                            field: 'prompt',
                            value: $event,
                            triggerView: 'historyBox'
                        })"
                        @unhover-prompt="controlStore.setHovered(null)"
                    />
                </div>
            </div>
            <div ref="miniMapContainer" class="flex-shrink-0 w-16">
                <VMiniMap v-if="renderMiniMap"
                    :canvas-width="minimapSize.width.value"
                    :canvas-height="minimapSize.height.value"
                    :records="records"
                    :links="promptPairs"
                    :stages="stages"
                    :similarity-matrix="similarityMatrix"
                    :hovered="hovered"
                    @hover-prompt="controlStore.setHovered({
                        field: 'prompt',
                        value: $event,
                        triggerView: 'miniMap'
                    })"
                    @unhover-prompt="controlStore.setHovered(null)"
                    @click-prompt="controlStore.setSelected({
                        field: 'prompt',
                        value: $event,
                        triggerView: 'miniMap'
                    })"
                    @update-stage="controlStore.segmentStages($event)"
                />
            </div>
        </div>
    </div>
</template>