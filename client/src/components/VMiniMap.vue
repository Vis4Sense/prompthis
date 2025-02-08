<script lang="ts" setup>
import type { PropType } from 'vue'
import { toRefs, watch, computed, ref } from 'vue'

import chroma from "chroma-js"
import { scaleLinear, arc } from 'd3'

interface Record {
    prompt: string
    [key: string]: any
}

interface Selector {
    field: string
    value: string | object | number
    triggerView: string
}

const props = defineProps({
    // canvas size
    canvasWidth: { // the width of the canvas
        type: Number as PropType<number>,
        default: 40
    },
    canvasHeight: { // the height of the canvas
        type: Number as PropType<number>,
        default: 400
    },
    paddingX: { // padding x
        type: Number as PropType<number>,
        default: 5,
    },
    // drawing parameters
    baseLineHeight: { // the default height of each record
        type: Number as PropType<number>,
        default: 20,
    },
    minRadius: { // the minimum radius of the circle
        default: 3,
    },
    maxRadiusRatio: { // the maximum radius of the circle (ratio to line height)
        default: 0.3,
    },
    colorScheme: { // the color scheme of the circles
        default: [
            "#d9d9d9",
            "#bdbdbd",
            "#969696",
            "#737373",
            "#525252",
            "#252525",
            "#000000",
        ]
    },
    // input data
    records: { // list of records
        type: Array as PropType<Record[]>,
        required: true,
    },
    links: { // list of links
        type: Array as PropType<[number, number][]> | null,
        default: null,
    },
    similarityMatrix: { // similarity matrix
        type: Array as PropType<number[][]> | null,
        default: null,
    },
    stages: { // list of stages
        type: Array as PropType<number[][]> | null,
        default: null,
    },
    // interaction
    hovered: {
        type: Object as PropType<Selector>,
        default: null,
    },
})

const {
    canvasWidth,
    canvasHeight,
    paddingX,
    baseLineHeight,
    minRadius,
    maxRadiusRatio,
    colorScheme,
} = props

const {
    records,
    links,
    similarityMatrix,
    hovered,
} = toRefs(props)

const emit = defineEmits([
    'hover-prompt',
    'unhover-prompt',
    'click-prompt',
    'update-stage'
])

/**
 * For calculating the position and size of points
 */

// calculate the height of each record
// currently the records are distributed evenly (vertical)
const lineHeight = computed(() => (
    Math.min(baseLineHeight * records.value.length, canvasHeight) / records.value.length
))

// compute the domains
const radiusDomain = computed(() => {
    const minPromptLen = Math.min(...records.value.map((record) => record.prompt.length))
    const maxPromptLen = Math.max(...records.value.map((record) => record.prompt.length))
    return [minPromptLen, maxPromptLen]
})

// compute the ranges
const radiusRange = computed(() => {
    const maxRadius = Math.max(minRadius, lineHeight.value * maxRadiusRatio)
    return [minRadius, maxRadius]
})

// compute the scales
const radiusScale = computed(() => (
    scaleLinear(radiusDomain.value, radiusRange.value)
))
const colorScale = computed(() => (
    chroma.scale(colorScheme).mode('lab').domain([0, records.value.length - 1])
))

/**
 * Points and links
 */

interface Point {
    x: number
    y: number
}
// points
const _points = computed(() => {
    return records.value.map((d, index) => ({
        ...d,
        x: canvasWidth / 2,
        y: lineHeight.value * index + lineHeight.value / 2,
    }))
})
// links
const _links = computed(() => {
    if (links.value === null) return []
    const highlightLinks = new Map()
    links.value.forEach(([source, target]) => {
        const sim = similarityMatrix.value[source][target]
        if (!highlightLinks.has(target) || highlightLinks.get(target).maxSim < sim) {
            highlightLinks.set(target, { maxSrc: source, maxSim: sim })
        }
    })
    const tmpLinks = links.value.map(([source, target]) => ({
        source: { id: source, x: _points.value[source].x, y: _points.value[source].y},
        target: { id: target, x: _points.value[target].x, y: _points.value[target].y},
    }))
    const dyMax = Math.max(...tmpLinks.map(({source, target}) => (
        Math.abs(source.y - target.y)
    ))) / 2
    const dxMax = Math.min(canvasWidth / 2 - paddingX, dyMax)
    const getArc = (p1: Point, p2: Point) => {
        const dy = Math.abs(p1.y - p2.y) / 2
        const dx = dxMax * dy / dyMax
        const radius = (dx * dx + dy * dy) / (2 * dx)
        const angle = Math.atan2(dy, radius - dx)
        const arcGenerator = arc()
            .innerRadius(radius)
            .outerRadius(radius)
            .startAngle(Math.PI + Math.PI / 2 - angle)
            .endAngle(Math.PI + Math.PI / 2 + angle)
        return {
            arc: arcGenerator(),
            offsetX: radius - dx,
        }
    }
    return tmpLinks.map(({source, target}) => ({
        source: { x: source.x, y: source.y},
        target: { x: target.x, y: target.y},
        ...getArc(source, target),
        highlight: highlightLinks.has(target.id) && highlightLinks.get(target.id).maxSrc === source.id,
    }))
})

// stage division
const hoveredSegment = ref(null as number | null)

// handle interaction
const hoveredPoint = ref(null as number | null)
const brushedPoints = ref([] as number[])

watch(hovered, (newVal, oldVal) => {
    brushedPoints.value = []
    if (newVal === null) {
        hoveredPoint.value = null
        return
    }
    const { field, value, triggerView } = newVal
    if (field === 'prompt') {
        hoveredPoint.value = value as number
    } else if (field === 'word') {
        if (oldVal) {
            const oldField = oldVal.field
            if (oldField === 'prompt') {
                hoveredPoint.value = oldVal.value as number
            }
        }
        const word = value.text as string
        brushedPoints.value = records.value
            .filter((record) => record.promptTokens.includes(word))
            .map((record) => record.promptId)
    } else if (field === 'image') {
        const { promptIndex } = value
        hoveredPoint.value = promptIndex
    }
})
</script>

<template>
    <svg :width="canvasWidth" :height="canvasHeight">
        <g class="minimap-stage-layer"
            :transform="`translate(${canvasWidth - 10}, 0)`"
        >
            <g class="minimap-stage"
                v-for="(stage, key) in stages"
                :key="key"
            >
                <rect
                    :x="-5"
                    :y="stage[0] * lineHeight + 2"
                    :width="5"
                    :height="(stage[stage.length-1] - stage[0] + 1) * lineHeight - 4"
                    :rx="5"
                    :ry="5"
                    :fill="colorScale(Math.ceil(
                        (stage[stage.length-1] + stage[0]) / 2
                    ))"
                    :fill-opacity="0.9"
                />
            </g>
            <g class="minimap-stage-segment"
                v-for="(_, key) in records"
                :key="key"
            >
                <rect v-if="key"
                    :x="-9"
                    :y="key * lineHeight - 4"
                    :rx="2"
                    :ry="2"
                    :width="13"
                    :height="8"
                    fill="#f0f0f0"
                    :fill-opacity="hoveredSegment === key ? 0.8 : 0"
                    stroke="#666666"
                    :stroke-opacity="hoveredSegment === key ? 1 : 0"
                    style="cursor: pointer;"
                    @mouseover="() => hoveredSegment = key"
                    @mouseout="() => hoveredSegment = null"
                    @click="() => emit('update-stage', key)"
                />
            </g>
        </g>
        <g
            class="minimap-link-layer"
        >
            <g
                class="minimap-link"
                v-for="({source, target, arc, offsetX, highlight}, key) in _links"
                :key="key"
                :transform="`translate(
                    ${canvasWidth / 2 + offsetX},
                    ${(source.y + target.y) / 2}
                )`"
            >
                <path
                    :d="arc"
                    fill="none"
                    stroke="#666"
                    :stroke-width="highlight ? 2 : 0.5"
                    :stroke-opacity="highlight ? 1 : 0.1"
                />
            </g>
        </g>
        <g class="minimap-point-layer">
            <g
                class="minimap-point"
                v-for="(point, key) in _points"
                :key="key"
            >
                <circle
                    :cx="point.x" :cy="point.y"
                    :r="radiusScale(point.prompt.length)"
                    :fill="hoveredPoint === key ? '#fbbf24' : colorScale(key)"
                    :stroke-width="2"
                    :stroke="brushedPoints.includes(key) ? '#fbbf24' : 'none'"
                    @mouseover="emit('hover-prompt', key)"
                    @mouseout="emit('unhover-prompt')"
                    @click="() => emit('click-prompt', key)"
                />
                <text
                    v-if="(key + 1) % 5 === 0"
                    :x="point.x + radiusScale(point.prompt.length) + 2"
                    :y="point.y + 5"
                    :font-size="10"
                    :fill="colorScale(key)"
                >{{ key + 1 }}</text>
            </g>
        </g>
    </svg>
</template>
