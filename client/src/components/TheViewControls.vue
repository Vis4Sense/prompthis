<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useStore as useControlStore } from '@/stores/control'

import VSlider from './VSlider.vue'

const controlStore = useControlStore()
const { embeddingWeight, minSimilarity, clusterThresh } = controlStore
const { edgeWeightMax, edgeWeightThresh } = storeToRefs(controlStore)
const { showIVG } = storeToRefs(controlStore)
const toggleIVG = () => {
    controlStore.toggleIVG()
}

const handleEmbeddingWeight = (value: number) => {
    controlStore.setEmbeddingWeight(value)
}
const handleEdgeWeightThreshChange = (value: number) => {
    controlStore.setEdgeWeightThresh(value)
}
const handleSimilarityChange = (value: number) => {
    controlStore.setMinSimilarity(value)
}
const handleClusterThreshChange = (value: number) => {
    controlStore.setClusterThresh(value)
}
</script>

<template>
    <div class="flex text-slate-50">
        <div class="px-3">
            <button class="border border-0.5 py-1 px-2 hover:bg-neutral-700 text-xs rounded" :class="{
                'bg-transparent': !showIVG,
                'bg-neutral-600': showIVG,
                'border-neutral-600': showIVG,
                'border-neutral-400': !showIVG,
                'text-neutral-400': !showIVG,
                'text-neutral-100': showIVG
            }" @click="toggleIVG">
                IVG
            </button>
        </div>
        <VSlider
            attribute-name="Embedding:"
            description-start="Text"
            description-end="Image"
            :fill-bar="false"
            :right-value="1"
            :precision="2"
            :default-value="embeddingWeight"
            @input="handleEmbeddingWeight"
        />
        <VSlider
            attribute-name="Prompt similarity"
            range-direction="upper"
            :right-value="1"
            :left-value="0.5"
            :precision="2"
            :default-value="minSimilarity"
            @input="handleSimilarityChange"
        />
        <VSlider
            attribute-name="Edge weight"
            range-direction="upper"
            :right-value="edgeWeightMax"
            :precision="2"
            :default-value="edgeWeightThresh"
            @input="handleEdgeWeightThreshChange"
        />
        <VSlider
            attribute-name="Cluster distance"
            :right-value="1"
            :precision="2"
            :default-value="clusterThresh"
            @change="handleClusterThreshChange"
        />
    </div>
</template>