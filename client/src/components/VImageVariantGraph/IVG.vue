<script lang="ts" setup>
import { computed, nextTick, ref, toRefs, watch, watchEffect } from 'vue'
import type { PropType } from 'vue'

import chroma from "chroma-js"
import { scaleLinear, sum, pie, arc, select, create, zoom as d3zoom, zoomIdentity } from 'd3'

import type { T2IRecord, Point, Node, Edge, EdgeGroup, WordChange, Selector, ImageSelector, WordSelectorValue, WordSelector, PromptSelector } from './types/IVG.d'
import { sortImagesByWeight } from './utils/weights'
import { rectIntersect } from './utils/graphics'
import { GraphicNode } from './graphics/node'
import { taperedEdge } from './graphics/edge'
import { bubbleOutline } from './graphics/bubble'
import { Annotator } from './utils/annotations'

import VClusterMinimap from './VClusterMinimap.vue'

import wordGlyphI from "@/assets/icons/i.png";
import wordGlyphR from "@/assets/icons/r.png";
import wordGlyphM from "@/assets/icons/m.png";
import wordGlyphIw from "@/assets/icons/iw.png";
import wordGlyphRw from "@/assets/icons/rw.png";

import legendDiffFrequency from '@/assets/legend/diff_frequency.svg'
import legendDiffWeight from '@/assets/legend/diff_weight.svg'

const wordModificationIcons = {
    i: wordGlyphI,
    r: wordGlyphR,
    m: wordGlyphM,
    iw: wordGlyphIw,
    rw: wordGlyphRw,
};

const props = defineProps({
    canvasWidth: {
        type: Number as PropType<number>,
        required: true,
    },
    canvasHeight: {
        type: Number as PropType<number>,
        required: true,
    },
    marginLeft: {
        type: Number,
        default: 50
    },
    marginRight: {
        type: Number,
        default: 50
    },
    marginBottom: {
        type: Number,
        default: 110
    },
    marginTop: {
        type: Number,
        default: 50
    },
    // control
    minEdgeWeight: {
        type: Number,
        default: 0.4,
    },
    idealEdgeGroupRange: {
        type: Array as PropType<number[]>,
        default: () => [6, 12],
    },
    // data
    records: {
        type: Array as PropType<T2IRecord[]>,
        required: true,
    },
    images: {
        type: Object,
        required: true,
    },
    projection: {
        type: Object,
        required: true,
    },
    clusters: {
        type: Object,
        required: true,
    },
    edges: {
        type: Array,
        required: true,
    },
    edgeGroups: {
        type: Object,
        required: true,
    },
    stages: {
        type: Array as PropType<number[][]> | null,
        default: null,
    },
    // style and theme
    bubbleStrokeWidth: {
        type: Number,
        default: 0.5,
    },
    bubbleStrokeOpacity: {
        type: Number,
        default: 0.7,
    },
    bubbleStrokeDasharray: {
        type: String,
        default: '2,2',
    },
    bubbleFillOpacity: {
        type: Number,
        default: 0,
    },
    edgeFill: {
        type: String,
        default: 'gray',
    },
    edgeFillOpacity: {
        type: Number,
        default: 0.2,
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
    colorFocus: { // the color of the focused circle
        default: '#fef08a'
    },
    colorBrushed: {
        default: 'white'
    },
    // mini map properties
    miniMapWidth: {
        type: Number,
        default: 100,
    },
    miniMapHeight: {
        type: Number,
        default: 100,
    },
    // interaction
    hovered: {
        type: Object as PropType<Selector>,
        default: null,
    }
})

const {
    idealEdgeGroupRange,
    colorScheme
} = props

const {
    canvasWidth,
    canvasHeight,
    marginLeft,
    marginRight,
    marginBottom,
    marginTop,
    minEdgeWeight,
    records,
    images,
    projection,
    clusters,
    edges,
    edgeGroups,
    stages,
    hovered
} = toRefs(props)

const imageEleId = (id: string) =>
    `ivg-image-${id.replace('(', '-').replace(')', '')}`

// compute nodes
const nodeData = computed(() => {
    const nodeId2Index = new Map()
    const record2nodeIndices = new Map()
    const nodes = [] as Node[]
    records.value.forEach((record: T2IRecord, index: number) => {
        const { outputFilenames, width, height } = record
        const indices = [] as number[]
        outputFilenames.forEach((filename) => {
            const id = filename.substring(0, filename.lastIndexOf('.'))
            nodeId2Index.set(id, nodes.length)
            indices.push(nodes.length)
            const image = images.value[filename]
            const { x, y } = projection.value[id]
            nodes.push({id, x, y, data: image, promptId: index, width, height})
        })
        record2nodeIndices.set(index, indices)
    })
    return { nodes, nodeId2Index, record2nodeIndices }
})

const nodes_ = computed(() => nodeData.value.nodes)
const record2nodeIndices = computed(() => nodeData.value.record2nodeIndices)

const ivgMain = ref<SVGElement>()
const ivgAnimation = ref<SVGElement>()
watch(nodes_, (newVal, oldVal) => {
    if (newVal.length === oldVal.length) return
    if (ivgMain.value === null) return
    if (oldVal.length === 0) {
        select(ivgMain.value)
            .attr('opacity', 0)
            .transition()
            .duration(1000)
            .attr('opacity', 1)
        return
    }
    // show animation layer
    ivgAnimation.value.innerHTML = ivgMain.value.innerHTML
    // hide main layer
    select(ivgMain.value)
        .attr('visibility', 'hidden')
    select(ivgAnimation.value)
        .attr('opacity', 1)
        .attr('visibility', 'visible')
    select(ivgAnimation.value)
        .selectAll('.no-transition')
        .attr('opacity', 1)
        .transition()
        .duration(1000)
        .attr('opacity', 0)
        .attr('visibility', 'hidden')
    // animation
    const layer = select(ivgAnimation.value)
    oldVal.forEach((node, idx) => {
        layer.select('#' + imageEleId(node.id))
            .transition()
            .duration(1000)
            .attr('transform', `translate(${xScale.value(newVal[idx].x)}, ${yScale.value(newVal[idx].y)})`)
    })
    setTimeout(() => {
        newVal.filter((_, idx) => idx >= oldVal.length)
            .forEach((node) => {
                layer
                    .append('g')
                    .attr('transform', `translate(${xScale.value(node.x)}, ${yScale.value(node.y)})`)
                    .append('image')
                    .attr('width', imageWidth.value)
                    .attr('x', - imageWidth.value / 2)
                    .attr('y', - imageWidth.value / 2)
                    .attr('xlink:href', 'data:image/png;base64,' + node.data)
                    .attr('opacity', 0)
                    .transition()
                    .duration(1000)
                    .attr('opacity', 1)
            })
    }, 1000);
    setTimeout(() => {
        select('.main-ivg')
            .attr('opacity', 0)
            .attr('visibility', 'visible')
            .transition()
            .duration(1000)
            .attr('opacity', 1)
        select(ivgAnimation.value)
            .attr('opacity', 1)
            .transition()
            .duration(1000)
            .attr('opacity', 0)
        setTimeout(() => {
            select(ivgAnimation.value)
                .attr('visibility', 'hidden')
        }, 1000)
    }, 2000)
})

const nodeId2Index = computed(() => nodeData.value.nodeId2Index)

// compute edges
const edges_ = computed(() => {
    const edges_ = edges.value as Edge[]
    return edges_.map((edge: Edge, idx) => ({
        ...edge,
        id: idx,
        src: nodeId2Index.value.get(edge.src),
        tgt: nodeId2Index.value.get(edge.tgt),
    })) as Edge[]
})
const edgeGroups_ = computed(() => (
    edgeGroups.value.map((group: EdgeGroup) => {
        // compute anchor position
        const subEdges = group.edges
            .map((d) => edges_.value[d]) as Edge[]
        const subEdgePoss = subEdges.map((d: Edge) => {
            const src = nodes_.value[d.src]
            const tgt = nodes_.value[d.tgt]
            const x = (src.x + tgt.x) / 2
            const y = (src.y + tgt.y) / 2
            const weight = d.weight / group.weight
            return { x, y, weight }
        })
        const x = sum(subEdgePoss, (d) => d.x * d.weight)
        const y = sum(subEdgePoss, (d) => d.y * d.weight)
        // group word changes
        const stPairs = subEdges.map((d) => {
            const src = nodes_.value[d.src]
            const tgt = nodes_.value[d.tgt]
            return [nodeId2Index.value.get(src.id), nodeId2Index.value.get(tgt.id)]
        })
        const allChanges = [] as WordChange[]
        stPairs.forEach(([src, tgt]) => {
            edges_.value.forEach((edge: Edge) => {
                if (edge.src === src && edge.tgt === tgt) {
                    const changes_ = edge.changes.map((change) => ({
                        ...change,
                        weight: edge.weight / edge.changes.length
                    })) as WordChange[]
                    allChanges.push(...changes_)
                }
            })
        })
        const allChangeMap = new Map()
        allChanges.forEach((change) => {
            const changeStr = change.action + '-' + change.word
            if (allChangeMap.has(changeStr)) {
                const oldVal = allChangeMap.get(changeStr)
                allChangeMap.set(changeStr, {
                    ...oldVal,
                    frequency: oldVal.frequency + 1,
                    weight: oldVal.weight + change.weight
                })
            } else {
                allChangeMap.set(changeStr, {
                    action: change.action,
                    word: change.word,
                    frequency: 1,
                    weight: change.weight,
                    included: false,
                })
            }
        })
        allChangeMap.forEach((value, key, map) => {
            map.set(key, {
                ...value,
                frequency: value.frequency / allChanges.length,
            })
        })
        const groupChanges = [] as WordChange[]
        subEdges.forEach((edge) => {
            const changes_ = edge.changes.map((change) => ({
                ...change,
                weight: edge.weight / edge.changes.length
            })) as WordChange[]
            groupChanges.push(...changes_)
        })
        groupChanges.forEach((change) => {
            const changeStr = change.action + '-' + change.word
            if (allChangeMap.has(changeStr)) {
                allChangeMap.set(changeStr, {
                    ...allChangeMap.get(changeStr),
                    included: true,
                })
            }
        })
        const changes_ = Array.from(allChangeMap.values())
            .sort((a, b) => {
                if (a.included && !b.included) return -1
                if (a.included && b.included) {
                    if (a.action === 'i' && b.action === 'r') return -1
                }
                return 1
            })
        return {
            ...group,
            changes: changes_,
            baryCenter: { x, y }
        }
    }) as EdgeGroup[]
))
const shownEdgeGroups = computed(() => (
    edgeGroups_.value.filter((group) => {
        const changes = group.changes
        const changes_ = changes.filter((d: WordChange) => d.included && d.weight >= minEdgeWeight.value)
        return changes_.length > 0
    }).map((group) => {
        const subEdges = group.edges.map((d) => ({...edges_.value[d]}))
        // group subedges according to source and target prompt
        const stPrompts = {} as Record<string, Edge[]>
        subEdges.forEach((edge) => {
            const key = edge.src_pmt + '-' + edge.tgt_pmt
            if (stPrompts[key]) {
                stPrompts[key].push(edge)
            } else {
                stPrompts[key] = [edge]
            }
        })
        // select one edge for each prompt pair
        for (const key in stPrompts) {
            const value = stPrompts[key]
            let flag = false
            for (const edge of value) {
                if (shownImages.value[edge.src] && shownImages.value[edge.tgt]) {
                    edge.display = true
                    flag = true
                    break
                } else if (shownImages.value[edge.src] || shownImages.value[edge.tgt]) {
                    edge.display = true
                    flag = true
                    break
                } else {
                    edge.display = false
                }
            }
            if (!flag) {
                value[0].display = true
            }
        }
        let shownEdges = subEdges.filter((d) => d.display)
        return {
            ...group,
            edges: shownEdges,
        }
    })
))

const isChangeShown = (d: WordChange) => (
    d.included && d.weight && d.weight >= minEdgeWeight.value
)

// use binary search to find threshold
const searchThresh = (minw, maxw) => {
    let minNum = idealEdgeGroupRange[0], maxNum = idealEdgeGroupRange[1]
    if (edgeGroups_.value.length === 0) return 0
    if (edgeGroups_.value.length < idealEdgeGroupRange[0]) minNum = 1
    let midw = (minw + maxw) / 2
    while (minw + 1e-6 < maxw) {
        const num = edgeGroups_.value.filter((group) => {
            const changes = group.changes
            const changes_ = changes.filter((d: WordChange) => d.weight >= midw)
            return changes_.length > 0
        }).length
        if (num < minNum) maxw = midw
        else if (num > maxNum) minw = midw
        else break
        midw = (minw + maxw) / 2
    }
    return midw
}

const emit = defineEmits([
    'update-weight-thresh',
    'update-max-weight',
    'hover-image',
    'unhover-image',
    'click-image',
    'open-image',
    'copy-prompt',
])

// compute image size and glyph size
const imageStrokeWidth = ref(2)
const scaleImageWidth = ref(1)

const imageWidth = computed(() => {
    if (!canvasWidth.value) return 50
    const minw = 40, maxw = 80
    let width = canvasWidth.value / 20
    width = Math.max(width, minw)
    width = Math.min(width, maxw)
    return width * scaleImageWidth.value
})

const imageGlyphWidth = computed(() => {
    if (!canvasWidth.value) return 10
    const minw = 8, maxw = 12
    let width = imageWidth.value / 5
    width = Math.max(width, minw)
    width = Math.min(width, maxw)
    return width * scaleImageWidth.value
})

// compute edge weight domain
const edgeWeightDomain = computed(() => {
    let maxWeight = 0.5
    edgeGroups_.value.forEach((group) => {
        group.changes.forEach((d: WordChange) => {
            if (d.weight && d.weight > maxWeight) maxWeight = d.weight
        })
    })
    const thresh = searchThresh(0, maxWeight)
    emit('update-weight-thresh', thresh)
    emit('update-max-weight', maxWeight)
    return [0, maxWeight]
})

// zoom transform
const transform = ref({
    x: 0,
    y: 0,
    k: 1,
})

// compute scales
const xScale = computed(() => {
    const scale = scaleLinear([0, 1], [marginLeft.value, canvasWidth.value - marginRight.value])
    return transform.value.rescaleX ? transform.value.rescaleX(scale) : scale
})
const yScale = computed(() => {
    const scale = scaleLinear([0, 1], [canvasHeight.value - marginBottom.value, marginTop.value])
    return transform.value.rescaleY ? transform.value.rescaleY(scale) : scale
})
const rScale = computed(() => (
    scaleLinear(edgeWeightDomain.value, [5, 12])
))
const colorScale = computed(() => (
    chroma.scale(colorScheme).mode('lab').domain([0, records.value.length - 1])
))

// instantiate graphicNode
const graphicNode = computed(() => {
    return new GraphicNode()
        .xScale(xScale.value)
        .yScale(yScale.value)
})

const annotator = computed(() => {
    return Annotator()
        .documents(records.value.map((record) => record.promptTokens || []))
})

// compute images to shown
const shownImages = computed(() => {
    const sortedImages = sortImagesByWeight(nodes_.value, edges_.value, edgeGroups_.value)
    const imgRects = nodes_.value.map((img) => ({
        x: xScale.value(img.x) - imageWidth.value / 2,
        y: yScale.value(img.y) - imageWidth.value / 2,
        width: imageWidth.value,
        height: imageWidth.value,
    }))
    const shownImages = nodes_.value.map(() => false)
    for (let i = 0, n = sortedImages.length; i < n; ++i) {
            let flag = true;
            for (let j = 0; j < i; ++j) {
                if (!shownImages[j]) continue;
                if (rectIntersect(imgRects[i], imgRects[j])) {
                    flag = false;
                }
            }
            if (!flag) continue;
            shownImages[i] = true;
        }
    return shownImages
})

/** Prompt and cluster bubbles */

// compute rects of image nodes
const nodes2rects = (nodes: Node[]) => (
    graphicNode.value.nodes(...nodes)
        .map((rect) => {
            const idx = nodeId2Index.value.get(rect.id)
            const shown = shownImages.value[idx]
            const width = shown ? imageWidth.value : imageGlyphWidth.value
            const height = width / rect.width * rect.height
            const x = rect.x - width / 2
            const y = rect.y - height / 2
            return { x, y, width, height }
        })
)

// compute bubble for given prompt id
const bubble = computed(() => {
    const bubble = (promptId: number) => {
        const nodeIndices = record2nodeIndices.value.get(promptId)
        const bubbleNodes = nodeIndices.map((nid) => nodes_.value[nid])
        const rects = nodes2rects(bubbleNodes)
        return { promptId, rects }
    }
    return bubble
})

// compute bubble for given cluster id
const clusterBubble = computed(() => {
    const clusterBubble = (clusterId: number) => {
        const nodeIndices = nodes_.value
            .filter((node) => clusters.value[node.id] === clusterId)
            .map((node) => nodeId2Index.value.get(node.id))
        const bubbleNodes = nodeIndices.map((nid) => nodes_.value[nid])
        const rects = nodes2rects(bubbleNodes)
        return { clusterId, rects }
    }
    return clusterBubble
})

// compute bubbles
const bubbles = computed(() => {
    if (records.value.length === 0) return []

    // if images generated by the same prompt are not in the same cluster
    const bubbleIndices = [] as number[]
    records.value.forEach((record, index) => {
        const clusterIds = record.outputFilenames.map((filename) => {
            const id = filename.substring(0, filename.lastIndexOf('.'))
            return clusters.value[id]
        })
        const uniqueClusterIds = Array.from(new Set(clusterIds))

        if (uniqueClusterIds.length > 1) {
            bubbleIndices.push(index)
        }
    })

    // include hovered prompt
    if (hoveredPrompt.value && !bubbleIndices.includes(hoveredPrompt.value)) {
        bubbleIndices.push(hoveredPrompt.value)
    }

    // get bubble rects
    const bubbles = bubbleIndices.map(d => bubble.value(d))

    return bubbles
})

/** Compute clusters */

const clusters_ = computed(() => {
    if (showGroupBubble.value === null) return []
    if (showGroupBubble.value === 'cluster') {
        const clusterIds = Array.from(new Set(Object.values(clusters.value)))
        const clusters_ = clusterIds.map((id) => {
            const bubble = clusterBubble.value(id)
            // annotation
            const prompts = Array.from(new Set(
                nodes_.value
                .filter((node) => clusters.value[node.id] === id)
                .map((node) => node.promptId)
            )).map((promptId) => records.value[promptId].promptTokens || [])
            const words = annotator.value
                .documentsToAnnotate(prompts)
                .annotate()
            const annotation = { words, position: { x: -100, y: -100, w: 0, h: 0}, html: '' }
            return { id, bubble, annotation }
        })
        nextTick(() => {
            updateClusterAnnotations()
        })
        return clusters_
    }
    else if (showGroupBubble.value === 'stage') {
        const clusters_ = stages.value.map((stage, id) => {
            const nodeIndices = [] as number[]
            stage.forEach((promptId) => {
                const indices = record2nodeIndices.value.get(promptId)
                nodeIndices.push(...indices)
            })
            const bubbleNodes = nodeIndices.map((nid) => nodes_.value[nid])
            const rects = nodes2rects(bubbleNodes)
            const bubble = { id, rects }
            // annotation
            const prompts = stage.map((promptId) => records.value[promptId].promptTokens || [])
            const words = annotator.value
                .documentsToAnnotate(prompts)
                .annotate()
            const annotation = { words, position: { x: -100, y: -100, w: 0, h: 0}, html: '' }
            const avgIdx = Math.ceil((stage[0] + stage[stage.length - 1]) / 2)
            return { id: avgIdx, bubble, annotation }
        })
        nextTick(() => {
            updateClusterAnnotations()
        })
        return clusters_
    }
    return []
})

const clusterAnnotations = ref([])
const updateClusterAnnotations = () => {
    const svgBbox = select('.ivg-svg').node().getBoundingClientRect()
    const shadowHost = select('.ivg-shadow').node()

    // bounding box of all bubbles
    const bubbleBboxes = clusters_.value.map(({id}) => {
        const bubbleEle = select(`#cluster-${id}`).select('path').node()
        const bbox = bubbleEle.getBoundingClientRect()
        return {
            x: bbox.x - svgBbox.x,
            y: bbox.y - svgBbox.y,
            width: bbox.width,
            height: bbox.height,
        }
    })
    const rects = [...bubbleBboxes]

    clusterAnnotations.value = clusters_.value.map(({id, annotation}) => {
        const pathEle = select(`#cluster-${id}`).select('path').node()
        const adiv = create('div')
            .style('width', '200px')
            .style('border', '0.5px solid #ddd')
            .style('border-radius', '2px')
            .style('padding', '0.2rem')
            .style('font-size', '0.5rem')
            .style('color', '#999')
            .style('background', 'rgba(255, 255, 255, 0.8)')
            .text(annotation.words.join(', '))
            .node()
        shadowHost.appendChild(adiv)
        const abbox = adiv.getBoundingClientRect()
        const bbox = pathEle.getBoundingClientRect()

        // find a position that does not overlap with other annotations
        const directions = [
            { dx: bbox.width + 1, dy: 0 },
            { dx: bbox.width + 1, dy: bbox.height / 2},
            { dx: bbox.width / 2, dy: bbox.height - 1 },
            { dx: 0, dy: bbox.height - 1 },
            { dx: - abbox.width - 1, dy: bbox.height - abbox.height },
            { dx: - abbox.width - 1, dy: bbox.height / 2},
            { dx: - abbox.width - 1, dy: 0},
            { dx: 0, dy: - abbox.height - 1 },
            { dx: bbox.width / 2, dy: - abbox.height - 1 },
        ]

        let position = { x: -100, y: -100, w: 0, h: 0 }

        for (const dir of directions) {
            const pos = {
                x: bbox.x - svgBbox.x + dir.dx,
                y: bbox.y - svgBbox.y + dir.dy,
                width: abbox.width,
                height: abbox.height,
            }
            let flag = true
            for (const rect of rects) {
                if (rectIntersect(pos, rect)) {
                    flag = false
                    break
                }
            }
            if (flag) {
                rects.push(pos)
                position = {
                    x: pos.x,
                    y: pos.y,
                    w: pos.width,
                    h: pos.height,
                }
                break
            }
        }

        const html = adiv.outerHTML
        return {...annotation, position, html}
    })
    select(shadowHost).selectAll('*').remove()
}

const pie_ = pie().value((d: WordChange) => d.frequency).sort(null)
const arc_ = (d) => {
    const arcGenerator = arc()
        .innerRadius(0)
        .outerRadius(rScale.value(d.data.weight))
    return arcGenerator(d)
}

const colorWordGlyph = {
    i: "#466E8F",
    r: "#CD3033",
    iw: "#466E8F",
    rw: "#CD3033",
    m: "#57B28F",
} as Record<string, string>

// drag
const isDragging = ref(false)
const glyphDragFuncs = {
    dragStart: function (event, d) {
        if (isDragging.value) return
        isDragging.value = true
        d.startX = event.x;
        d.startY = event.y;
        d.offsetX = d.offsetX || xScale.value(d.baryCenter.x);
        d.offsetY = d.offsetY || yScale.value(d.baryCenter.y);
    },
    dragging: function (event, d) {
        if (!isDragging.value) return
        if (!d.startX || !d.startY) return
        const dx = event.x - d.startX;
        const dy = event.y - d.startY;
        d.offsetX += dx;
        d.offsetY += dy;

        select('#word-glyph-' + d.idx)
            .attr('transform', `translate(${d.offsetX}, ${d.offsetY})`)
        d.edges.forEach((edge: Edge) => {
            select(`#edge-${edge.id}`)
                .select('path')
                .attr('d', taperedEdge(
                    graphicNode.value.node(nodes_.value[edge.src]),
                    graphicNode.value.node(nodes_.value[edge.tgt]),
                    graphicNode.value.node({ x: d.offsetX, y: d.offsetY}, false),
                ))
        })

        d.startX = event.x;
        d.startY = event.y;
    },
    dragEnd: (event, d) => {
        isDragging.value = false
        delete d.startX;
        delete d.startY;
    },
}

// text annotation position
const textPosition = (change) => {
    const radius = rScale.value(change.data.weight)
    if (0 <= change.startAngle && change.startAngle < Math.PI / 2) return { x: radius * 1.2, y: 0 }
    return { x: 0, y: radius * 1.2 + 10}
}

/** control layer visibility */

const showPromptBubble = ref(true)
const showGroupBubble = ref('cluster' as 'cluster' | 'stage' | null)
const showAnnotation = ref(true)
const showDiffEdge = ref(true)

/** handle interaction */

const hoveredNode = ref(null as string | null)
const brushedNodes = ref({} as Record<string, string>)
const hoveredWord = ref(null as WordSelectorValue | null)
const hoveredPrompt = ref(null as number | null)
const hoveredEdge = ref(null as Edge | null)
const brushedEdges = ref([] as number[])

const tooltipContent = computed(() => {
    if (!hoveredNode.value) return null
    if (hovered.value && hovered.value.triggerView !== 'ivg') return null
    const nodeIndex = nodeId2Index.value.get(hoveredNode.value)
    const node = nodes_.value[nodeIndex]
    const { data, promptId } = node
    const record = records.value[promptId]
    const { prompt } = record
    return { promptId, prompt, data }
})

const tooltipPosition = ref({ x: 0, y: 0 })

const handleHoverNode = (event, node: Node | null = null) => {
    if (!node) {
        emit('unhover-image', null)
    } else {
        emit('hover-image', {
            imageId: node.id,
            imageIndex: nodeId2Index.value.get(node.id),
            promptIndex: node.promptId,
        })
    }
    hoveredNode.value = node?.id || null
    if (node) {
        hoveredPrompt.value = node.promptId

        // calculate tooltip position
        nextTick(() => {
            const mainDiv = select('.ivg-container').node()
            const mainBbox = mainDiv.getBoundingClientRect()
            const { x, y } = event
            const offsetX = x - mainBbox.x
            const offsetY = y - mainBbox.y
            const tooltipDiv = select('.tooltip').node()
            const tooltipBbox = tooltipDiv.getBoundingClientRect()
            const { width, height } = tooltipBbox
            const padx = imageWidth.value
            const pady = 10
            if (offsetX + width + padx > mainBbox.width) {
                tooltipPosition.value.x = offsetX - width - padx
            } else {
                tooltipPosition.value.x = offsetX + padx
            }
            if (offsetY + height + pady > mainBbox.height) {
                tooltipPosition.value.y = offsetY - height - pady
            } else {
                tooltipPosition.value.y = offsetY + pady
            }
        })
    }
}
const handleClickNode = (node: Node) => {
    const { id, promptId } = node
    emit('click-image', {
        imageId: id,
        imageIndex: nodeId2Index.value.get(id),
        promptIndex: promptId,
    })
}
const handleHoverBubble = (promptId: number | null = null) => {
    hoveredPrompt.value = promptId
}
const handleHoverWord = (word: WordSelectorValue | null = null) => {
    hoveredWord.value = word
    brushNodesForWord(word)
}

const brushNodesForWord = (word: WordSelectorValue | null) => {
    brushedNodes.value = {}
    brushedEdges.value = []

    if (!word) return

    const records_ = records.value as T2IRecord[]
    nodes_.value.forEach((node) => {
        if (records_[node.promptId].promptTokens.includes(word.text)) {
            brushedNodes.value[node.id] = 'white'
        }
    })
    // filter edges that contain the word
    shownEdgeGroups.value.forEach((edgeGroup) => {
        const subEdges = edgeGroup.edges
        subEdges.forEach((edge) => {
            const changes_ = edge.changes.filter((change) => (
                change.word === word.text
                && (word.action === null || word.action === 'k' || change.action === word.action)
            ))
            if (changes_.length > 0) {
                brushedEdges.value.push(edge.id)
            }
        })
    })

    brushedEdges.value.forEach((edgeId) => {
        const edge = edges_.value[edgeId]
        const action = edge.changes.find((change) => (
            change.word === word.text
            && (word.action === null || word.action === 'k' || change.action === word.action)
        ))?.action
        const src = nodes_.value[edge.src].id
        const tgt = nodes_.value[edge.tgt].id
        if (action === 'r') {
            brushedNodes.value[src] = 'steelblue'
            brushedNodes.value[tgt] = 'rgb(241, 41, 41)'
        } else if (action === 'i') {
            brushedNodes.value[src] = 'rgb(241, 41, 41)'
            brushedNodes.value[tgt] = 'steelblue'
        } else if (action === 'm') {
            brushedNodes.value[tgt] = 'mediumaquamarine'
        } else if (action === 'iw') {
            brushedNodes.value[src] = 'steelblue'
        } else if (action === 'rw') {
            brushedNodes.value[src] = 'rgb(241, 41, 41)'
        }
    })
}

// handle hover changes
watch(hovered, (newVal, oldVal) => {
    if (!newVal) {
        hoveredNode.value = null
        hoveredWord.value = null
        hoveredPrompt.value = null
        brushedNodes.value = {}
        brushedEdges.value = []
        return
    }
    if (newVal.field === 'image') {
        const selector = newVal as ImageSelector
        const { imageId, promptIndex } = selector.value
        hoveredNode.value = imageId
        hoveredPrompt.value = promptIndex
    } else if (newVal.field === 'word') {
        const selector = newVal as WordSelector
        hoveredWord.value = selector.value
        brushNodesForWord(selector.value)
        // if hover word from prompt
        if (oldVal && oldVal.field === 'prompt') {
            const promptId = (oldVal as PromptSelector).value
            hoveredPrompt.value = promptId
        }
    } else if (newVal.field === 'prompt') {
        const selector = newVal as PromptSelector
        hoveredPrompt.value = selector.value
    }
})

/** Zoom */

const zoomed = (event) => {
    const trans = event.transform
    transform.value = trans
    const { k } = trans
    if (k > 3) {
        scaleImageWidth.value = Math.min(k / 3, 2)
    } else {
        scaleImageWidth.value = 1
    }
}

const zoom = d3zoom()
    .scaleExtent([0.8, 15])
    .on('zoom', zoomed)

watchEffect(() => {
    if (ivgMain.value === null) return
    select(ivgMain.value).select('rect.zoom-canvas')
        .call(zoom)
        .call(zoom.transform, zoomIdentity)
})
</script>

<template>
<div class="ivg-container">
    <div class="ivg-shadow" style="position:absolute;left:-1000px;top:-1000px"></div>
    <svg
        :viewBox="`0, 0, ${canvasWidth}, ${canvasHeight}`"
        @mouseup="isDragging = false"
        @mouseleave="isDragging = false"
        class="ivg-svg"
    >
        <defs>
            <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="black" />
            </marker>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="4" dy="4" stdDeviation="4" flood-color="rgba(0,0,0,0.4)" />
            </filter>
        </defs>
        <g class="main-ivg" ref="ivgMain">
            <rect class="zoom-canvas"
                :width="canvasWidth"
                :height="canvasHeight"
                fill="white"
                :opacity="0"
                @mouseover="() => {
                    emit('unhover-image', null)
                    // todo: need to refactor
                    hoveredNode = null
                    hoveredWord = null
                    hoveredPrompt = null
                    brushedNodes = {}
                    brushedEdges = []
                }"
            />
            <g class="ivg-cluster-bubble-layer no-transition" v-if="showGroupBubble !== null">
                <g class="ivg-cluster"
                    v-for="({id, bubble}, index) in clusters_" :key="index"
                    :id="`cluster-${id}`"
                >
                    <path
                        :d="bubbleOutline(bubble.rects)"
                        :fill="showGroupBubble === 'stage' ? colorScale(id) : 'gray'"
                        :fill-opacity="showGroupBubble === 'stage' ? 0.3 : 0.1"
                    />
                </g>
            </g>
            <g class="ivg-bubble-layer no-transition">
                <g class="ivg-bubble"
                    v-for="(bubble, index) in bubbles"
                    :key="index"
                    @mouseenter="handleHoverBubble(bubble.promptId)"
                    @mouseleave="handleHoverBubble()"
                >
                    <path
                        v-if="showPromptBubble || hoveredPrompt === bubble.promptId"
                        :d="bubbleOutline(bubble.rects)"
                        :stroke="bubble.promptId !== hoveredPrompt
                            ? colorScale(bubble.promptId) : '#f59e0b'
                        "
                        :stroke-width="bubble.promptId !== hoveredPrompt
                            ? bubbleStrokeWidth : Math.max(bubbleStrokeWidth * 2, 2)
                        "
                        :stroke-opacity="bubbleStrokeOpacity"
                        :stroke-dasharray="bubbleStrokeDasharray"
                        :fill="bubble.promptId !== hoveredPrompt
                            ? colorScale(bubble.promptId) : colorFocus
                        "
                        :fill-opacity="bubble.promptId !== hoveredPrompt
                            ? bubbleFillOpacity : 0.5
                        "
                    />
                </g>
            </g>
            <g class="ivg-edge-layer no-transition" ref="edgeLayer"
                v-if="showDiffEdge"
            >
                <g class="ivg-edge-group"
                    v-for="(group, index) in shownEdgeGroups" :key="index"
                    :id="`edge-group-${group.idx}`"
                >
                    <g class="ivg-edge"
                        v-for="(edge, idx) in group.edges" :key="idx"
                        :id="`edge-${edge.id}`"
                    >
                        <path
                            :d="taperedEdge(
                                graphicNode.node(nodes_[edge.src]),
                                graphicNode.node(nodes_[edge.tgt]),
                                graphicNode.node(group.baryCenter),
                            )"
                            :fill="brushedEdges.includes(edge.id) ? '#fbbf24' : edgeFill"
                            :fill-opacity="edgeFillOpacity"
                        />
                    </g>
                </g>
            </g>
            <g class="ivg-image-layer">
                <g class="ivg-image"
                    v-for="node in nodes_"
                    :key="node.id"
                    :transform="'translate(' + xScale(node.x) + ',' + yScale(node.y) + ')'"
                    :id="imageEleId(node.id)"
                    @mouseenter="(e) => handleHoverNode(e, node)"
                    @mouseleave="handleHoverNode(e)"
                >
                    <rect
                        v-if="
                            hoveredNode === node.id
                            || (brushedNodes[node.id] && shownImages[nodeId2Index.get(node.id)])
                        "
                        :width="imageWidth + imageStrokeWidth * 4"
                        :height="imageWidth / node.width * node.height + imageStrokeWidth * 4"
                        :x="- imageWidth / 2 - imageStrokeWidth * 2"
                        :y="- imageWidth / node.width * node.height / 2 - imageStrokeWidth * 2"
                        :fill="hoveredNode === node.id ? colorFocus : brushedNodes[node.id] || colorBrushed"
                        filter="url(#shadow)"
                    />
                    <rect
                        v-if="shownImages[nodeId2Index.get(node.id)] || hoveredNode === node.id"
                        :width="imageWidth + imageStrokeWidth * 2"
                        :height="imageWidth / node.width * node.height + imageStrokeWidth * 2"
                        :x="- imageWidth / 2 - imageStrokeWidth"
                        :y="- imageWidth / node.width * node.height / 2 - imageStrokeWidth"
                        :fill="colorScale(node.promptId)"
                    />
                    <image
                        v-if="shownImages[nodeId2Index.get(node.id)] || hoveredNode === node.id"
                        @click="handleClickNode(node)"
                        :width="imageWidth"
                        :x="- imageWidth / 2"
                        :y="- imageWidth / node.width * node.height / 2"
                        :xlink:href="'data:image/jpeg;base64,' + node.data"
                    />
                    <g class="ivg-image-button"
                        v-if="hoveredNode === node.id && hovered && hovered.triggerView === 'ivg'"
                        style="cursor: pointer;"
                    >
                        <g
                            @click="emit('open-image', {
                                data: node.data,
                                filename: node.id,
                            })"
                        >
                            <rect class="ivg-full-button"
                                :width="imageWidth * 2 / 3"
                                :height="20"
                                :x="- imageWidth / 3"
                                :y="- 22"
                                :rx="4"
                                :ry="4"
                                :fill-opacity="0.7"
                            />
                            <text
                                :y="-12"
                                text-anchor="middle"
                                alignment-baseline="middle"
                                font-size="10"
                                fill="white"
                            >Full</text>
                        </g>
                        <g
                            @click="emit('copy-prompt', records[node.promptId].prompt)"
                        >
                            <rect class="ivg-full-button"
                                :width="imageWidth * 2 / 3"
                                :height="20"
                                :x="- imageWidth / 3"
                                :y="2"
                                :rx="4"
                                :ry="4"
                                :fill-opacity="0.7"
                            />
                            <text
                                :y="12"
                                text-anchor="middle"
                                alignment-baseline="middle"
                                font-size="10"
                                fill="white"
                            >Copy</text>
                        </g>
                    </g>
                    <rect
                        v-if="!shownImages[nodeId2Index.get(node.id)] && hoveredNode !== node.id"
                        :width="imageGlyphWidth"
                        :height="imageGlyphWidth / node.width * node.height"
                        :x="- imageGlyphWidth / 2"
                        :y="- imageGlyphWidth / 2"
                        :fill="colorScale(node.promptId)"
                    />
                </g>
                <use v-if="hoveredNode" :xlink:href="'#' + imageEleId(hoveredNode)" />
            </g>
            <g class="ivg-cluster-annotation-layer no-transition" v-if="showGroupBubble !== null && showAnnotation">
                <g class="ivg-cluster-annotation"
                    v-for="({id, position, html}, index) in clusterAnnotations" :key="index"
                    :id="`cluster-annotation-${id}`"
                >
                    <foreignObject
                        :x="position.x"
                        :y="position.y"
                        :width="position.w"
                        :height="position.h"
                    >
                        <div v-html="html" />
                    </foreignObject>
                </g>
            </g>
            <g class="ivg-word-layer no-transition" ref="wordLayer"
                v-if="showDiffEdge"
            >
                <g class="ivg-word"
                    v-for="(group, index) in shownEdgeGroups"
                    :key="index"
                    :id="`word-glyph-${group.idx}`"
                    :transform="'translate(' + xScale(group.baryCenter.x) + ',' + yScale(group.baryCenter.y) + ')'"
                    style="cursor: pointer;"
                    @mousedown="glyphDragFuncs.dragStart($event, group)"
                    @mousemove="glyphDragFuncs.dragging($event, group)"
                    @mouseup="glyphDragFuncs.dragEnd($event, group)"
                >
                    <g class="ivg-word-glyph">
                        <g class="ivg-word-glyph-component"
                            v-for="(change, idx) in pie_(group.changes)"
                            :key="idx"
                        >
                            <path
                                :d="arc_(change)"
                                :fill="change.data.included ? colorWordGlyph[change.data.action] : 'white'"
                                :stroke="!change.data.included ? colorWordGlyph[change.data.action] : 'white'"
                                :fill-opacity="change.data.weight >= minEdgeWeight ? 1 : 0.1"
                                :stroke-opacity="change.data.weight >= minEdgeWeight ? 1 : 0.1"
                            />
                            <g
                                v-if="isChangeShown(change.data) && idx < 3"
                                :transform="`translate(
                                    ${rScale(change.data.weight) * 1.2},
                                    ${idx * 14}
                                )`"
                            >
                                <image
                                    :y="-15"
                                    :width="10"
                                    :xlink:href="wordModificationIcons[change.data.action]"
                                />
                                <text
                                    x="10"
                                    :stroke="hoveredWord?.text === change.data.word ? colorFocus : 'white'"
                                    stroke-width="3"
                                    font-size="0.7rem"
                                    style="paint-order: stroke fill; font-weight: 300;"
                                    :style="hoveredWord?.text === change.data.word ? 'font-weight: bold;' : 'font-weight: 300;'"
                                    @mouseenter="handleHoverWord({action: change.data.action, text: change.data.word})"
                                    @mouseleave="handleHoverWord()"
                                >{{ change.data.word }}</text>
                            </g>
                        </g>
                    </g>
                </g>
            </g>
        </g>
        <g class="animation-ivg" ref="ivgAnimation"></g>
        <VClusterMinimap
            transform="translate(5,5)"
            :nodes="nodes_"
            :clusters="clusters"
        />
    </svg>
    <div class="legend px-2 flex justify-between items-strech">
        <div class="legend-node py-1 space-y-1">
            <div class="px-1 flex justify-between items-center">
                <div class="legend-text font-bold">Generated image (node)</div>
                <button :class="{'active': showAnnotation}"
                    @click="showAnnotation = !showAnnotation"
                >annotation</button>
            </div>
            <div class="px-1 flex space-x-2">
                <div class="legend-text">Steps:</div>
                <div class="legend-color-scale flex flex-auto items-center space-x-2">
                    <div class="legend-text">1</div>
                    <div class="gradient-bar flex-1"></div>
                    <div class="legend-text">{{ records.length || 1 }}</div>
                </div>
            </div>
            <div class="legend-bubble-container px-1 flex items-center space-x-2">
                <div class="legend-bubble flex">
                    <div class="bubble-rect legend-bubble-prompt"></div>
                </div>
                <div class="legend-text">Images generated by same prompt</div>
                <div class="button-group">
                    <button :class="{'active': showPromptBubble}"
                        @click="showPromptBubble = true"
                    >show</button>
                    <button :class="{'active': !showPromptBubble}"
                        @click="showPromptBubble = false"
                    >hide</button>
                </div>
            </div>
            <div class="legend-bubble-container px-1 flex items-center space-x-2">
                <div class="legend-bubble flex">
                    <div class="bubble-rect legend-bubble-group"></div>
                </div>
                <div class="legend-text">Images grouped by</div>
                <div class="button-group">
                    <button :class="{'active': showGroupBubble === 'cluster'}"
                        @click="showGroupBubble = 'cluster'"
                    >cluster</button>
                    <button :class="{'active': showGroupBubble === 'stage'}"
                        @click="showGroupBubble = 'stage'"
                    >exploration stage</button>
                    <button :class="{'active': showGroupBubble === null}"
                        @click="showGroupBubble = null"
                    >hide</button>
                </div>
            </div>
        </div>
        <div class="legend-edge flex flex-col py-1">
            <div class="px-1 mb-1 flex justify-between items-center">
                <div class="legend-text font-bold">Prompt difference (edge)</div>
                <button :class="{'active': showDiffEdge}"
                    @click="showDiffEdge = !showDiffEdge"
                >edge</button>
            </div>
            <div class="flex-1 flex space-x-2 px-1">
                <div class="flex flex-col justify-between">
                    <div class="legend-edge-direction flex space-x-1 items-center">
                        <div class="legend-text">Old</div>
                        <div class="triangle"></div>
                        <div class="legend-text">New</div>
                    </div>
                    <div class="legend-edge-frequency flex space-x-1 items-center">
                        <img :src="legendDiffFrequency"/>
                        <div class="legend-text">Diff frequency</div>
                    </div>
                    <div class="legend-edge-weight flex space-x-1 items-center">
                        <img :src="legendDiffWeight"/>
                        <div class="legend-text">Diff weight</div>
                    </div>
                </div>
                <div class="flex flex-col justify-between">
                    <div class="legend-glyph-row flex px-1 space-x-1 justify-end">
                        <div class="legend-glyph flex space-x-0.5 items-center">
                            <img :src="wordModificationIcons['m']"/>
                            <div class="legend-text">Reorder</div>
                        </div>
                    </div>
                    <div class="legend-glyph-row flex px-1 space-x-1 justify-end">
                        <div class="legend-glyph flex space-x-0.5 items-center">
                            <img :src="wordModificationIcons['i']"/>
                            <div class="legend-text">Insert</div>
                        </div>
                        <div class="legend-glyph flex space-x-0.5 items-center">
                            <img :src="wordModificationIcons['iw']"/>
                            <div class="legend-text">Increase weight</div>
                        </div>
                    </div>
                    <div class="legend-glyph-row flex px-1 space-x-1 justify-end">
                        <div class="legend-glyph flex space-x-0.5 items-center">
                            <img :src="wordModificationIcons['r']"/>
                            <div class="legend-text">Remove</div>
                        </div>
                        <div class="legend-glyph flex space-x-0.5 items-center">
                            <img :src="wordModificationIcons['rw']"/>
                            <div class="legend-text">Reduce weight</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="tooltip flex space-x-2 p-2 bg-white bg-opacity-90"
        v-if="tooltipContent"
        :style="{
            'top': tooltipPosition.y + 'px',
            'left': tooltipPosition.x + 'px',
        }"
    >
        <div class="tooltip-image flex-shrink-0">
            <img :src="'data:image/png;base64,' + tooltipContent.data" />
        </div>
        <div class="tooltip-prompt">
            <span>{{ tooltipContent.promptId + 1 + '. ' }}</span>
            <span>{{ tooltipContent.prompt }}</span>
        </div>
    </div>
</div>
</template>

<style scoped>
.fade-move, .fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.ivg-container {
    position: relative;
}

image {
    cursor: pointer;
}

.legend {
    position: absolute;
    width: auto;
    height: auto;
    left: 5px;
    right: 5px;
    bottom: 5px;
    font-size: 0.65rem;
    background-color: #e5e5e535;
    border: #e5e5e5 1px solid;
}

.triangle {
    width: 0;
    height: 0;
    border-top: 0.2rem solid transparent;
    border-bottom: 0.2rem solid transparent;
    border-left: 2.5rem solid #66666640;
}

.bubble-rect {
    width: 1rem;
    height: 1rem;
    border-radius: 0.4rem;
}

.legend-bubble-prompt {
    border: 1px dashed #999;
}

.legend-bubble-group {
    background-color: #999;
    opacity: 0.15;
}

.gradient-bar {
    width: 100%;
    height: 0.4rem;
    background: linear-gradient(to right, #d9d9d9, #000000);
}

button {
    background-color: #fafafa;
    border: 1px solid #e5e5e5;
    color: #a3a3a3;
    cursor: pointer;
    font-size: 0.6rem;
    padding-left: 0.2rem;
    padding-right: 0.2rem;
}

button:hover {
    background-color: #bcbcbc;
    border: 1px solid #ddd;
    color: #fafafa;
}

button.active {
    background-color: #919191;
    border: 1px solid #ddd;
    color: #fafafa;
}

.button-group button:not(:last-child) {
  border-right: none;
}

.button-group button:first-child {
    border-radius: 0.2rem 0 0 0.2rem;
}

.button-group button:last-child {
    border-radius: 0 0.2rem 0.2rem 0;
}

.legend-glyph-row {
    height: 1.1rem;
}

.legend-glyph img {
    width: 0.7rem;
    margin-top: -0.1rem;
}

.tooltip {
    position: absolute;
    width: 18rem;
    font-size: 0.7rem;
    box-shadow: rgba(50, 50, 93, 0.25) 0px 2px 5px -1px, rgba(0, 0, 0, 0.3) 0px 1px 3px -1px;
}
</style>
