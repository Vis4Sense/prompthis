<script lang="ts" setup>
import { computed, toRefs, type PropType } from 'vue'

import { scaleLinear, scaleOrdinal, schemeCategory10 } from 'd3'

interface Node {
    id: string,
    x: number,
    y: number,
    [key: string]: any,
}

const props = defineProps({
    canvasWidth: {
        type: Number as PropType<number>,
        default: 100,
    },
    canvasHeight: {
        type: Number as PropType<number>,
        default: 100,
    },
    canvasBorderColor: {
        type: String,
        default: '#e5e5e5',
    },
    canvasBorderWidth: {
        type: Number,
        default: 1,
    },
    canvasBackground: {
        type: String,
        default: '#e5e5e535',
    },
    canvasPadding: {
        type: Number,
        default: 10,
    },
    // data
    nodes: {
        type: Array as PropType<Node[]>,
        required: true,
    },
    clusters: {
        type: Object,
        required: true,
    },
})

const {
    canvasWidth,
    canvasHeight,
    canvasPadding
} = props

const {
    nodes,
    clusters
} = toRefs(props)

const clusterCount = computed(() => {
    const clusterSet = new Set()
    nodes.value.forEach(node => {
        clusterSet.add(clusters.value[node.id])
    })
    return clusterSet.size
})

// scale functions
const xScale = computed(() => (
    scaleLinear([0, 1], [canvasPadding, canvasWidth - canvasPadding])
))
const yScale = computed(() => (
    scaleLinear([0, 1], [canvasHeight - canvasPadding, canvasPadding])
))
const clusterColorScale = scaleOrdinal(schemeCategory10)
</script>

<template>
    <g>
        <rect
            :width="canvasWidth"
            :height="canvasHeight"
            :fill="canvasBackground"
            :stroke="canvasBorderColor"
            :stroke-width="canvasBorderWidth"
        />
        <g>
            <g
                v-for="(node, idx) in nodes"
                :key="idx"
                :transform="`translate(${xScale(node.x)}, ${yScale(node.y)})`"
            >
                <circle
                    :r="2"
                    :fill-opacity="0.5"
                    :fill="clusterColorScale(clusters[node.id])"
                />
            </g>
        </g>
        <text
            :transform="`translate(${canvasPadding / 2}, ${canvasHeight - canvasPadding / 2})`"
            :font-size="10"
        >{{ clusterCount + ' clusters' }}</text>
    </g>
</template>
