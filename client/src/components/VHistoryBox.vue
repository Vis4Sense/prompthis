<script lang="ts" setup>
import { ref, toRefs, watch, nextTick, onMounted } from 'vue'
import type { PropType } from 'vue'

import copyIcon from '@/assets/icons/copy.svg'
import rawIcon from '@/assets/icons/raw.svg'
import shrinkIcon from '@/assets/icons/shrink.svg'

import VLoading from './VLoading.vue'

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

interface RecordMeta {
    promptId: number
    prompt: string
    promptTokens: string[]
    promptTokenDiff: DiffWord[]
    [key: string]: any
}

interface RecordDetail {
    id: string
    data: string
}

interface HbRecord {
    meta: RecordMeta
    details: RecordDetail[]
}

interface Selector {
    field: string
    value: string | object
    triggerView: string
}

const props = defineProps({
    records: {
        type: Array as PropType<HbRecord[]>,
        required: true,
    },
    cache: {
        type: Object as PropType<HbRecord>,
        default: null,
    },
    hovered: {
        type: Object as PropType<Selector>,
        default: null,
    },
    selected: {
        type: Array as PropType<Selector[]>,
        default: () => [],
    }
})

const {
    records,
    cache,
    selected,
    hovered,
} = toRefs(props)

const recordContainer = ref<HTMLDivElement>()

const showCopyIcon = ref(records.value.map(() => false))
const showRawPrompt = ref(records.value.map(() => false))

const scrollToBottom = () => {
    if (recordContainer.value) {
        recordContainer.value.scrollTop = recordContainer.value.scrollHeight
    }
}

const updateCopyIcon = (key: number, value: boolean) => {
    showCopyIcon.value[key] = value
}

const hoverPrompt = (promptId: number, isenter: boolean = true) => {
    updateCopyIcon(promptId, isenter)
    if (isenter) emit('hover-prompt', promptId)
    else emit('unhover-prompt', null)
}

watch(records, () => {
    nextTick(scrollToBottom)
})

watch(selected, () => {
    if (selected.value.length === 0) return
    const selector = selected.value[0]
    const { field, value, triggerView } = selector
    if (field === 'image') {
        const { promptIndex } = value
        // scroll
        const targetDiv = document.getElementById('hbrecord-' + promptIndex)
        if (targetDiv) {
            targetDiv.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center',
            })
        }
    } else if (field === 'prompt') {
        const targetDiv = document.getElementById('hbrecord-' + value)
        if (targetDiv) {
            targetDiv.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center',
            })
        }
    }
})

const hoveredPrompt = ref(null as number | null)
const hoveredImage = ref(null as { promptIndex: number, imageIndex: number, imageId: string } | null)

watch(hovered, () => {
    if (hovered.value === null) {
        hoveredPrompt.value = null
        hoveredImage.value = null
        return
    }
    const { field, value, triggerView } = hovered.value
    if (field === 'image') {
        const { promptIndex, imageIndex } = value
        hoveredPrompt.value = promptIndex
        hoveredImage.value = value
    } else if (field === 'prompt') {
        hoveredPrompt.value = value
    }
})

onMounted(() => {
    nextTick(scrollToBottom)
})

const emit = defineEmits(['open-image', 'copy-prompt', 'hover-image', 'unhover-image', 'hover-word', 'unhover-word', 'hover-prompt', 'unhover-prompt'])
</script>

<template>
    <div class="w-full h-full border-l-1 border-r-1 border-neutral-400 py-2 ">
        <div
            class="h-full overflow-y-auto smooth-scroll"
            ref="recordContainer"
        >
            <div class="hbrecord"
                v-for="({ meta, details }, key) in records"
                :key="key"
                :id="'hbrecord-' + key"
            >
                <div class="hbrecord-prompt px-2 py-0 text-sm text-neutral-900">
                <div class="relative p-1 border rounded-md transition duration-300 ease-in-out transform hover:border-amber-200 hover:bg-amber-200 hover:bg-opacity-10"
                    :class="{
                        'border-transparent': hoveredPrompt !== key,
                        'border-amber-200 bg-amber-200 bg-opacity-10': hoveredPrompt === key,
                    }"
                    @mouseenter="hoverPrompt(key, true)"
                    @mouseleave="hoverPrompt(key, false)"
                >
                    <div v-if="!meta.promptTokenDiff || !meta.promptTokens">
                        <span>{{ meta.promptId + 1 + '. ' }}</span>
                        <span>{{ meta.prompt }}</span>
                    </div>
                    <div v-else-if="!meta.showDiff">
                        <span>{{ meta.promptId + 1 + '. ' }}</span>
                        <span
                            v-for="(word, widx) in meta.promptTokens"
                            :key="'hbrecord-' + key + '-' + widx"
                            class="hover:bg-amber-200 cursor-pointer"
                            @mouseenter="emit('hover-word', {
                                action: null,
                                text: word
                            })"
                            @mouseleave="emit('hover-prompt', key)"
                        >
                            {{ word + ' ' }}
                        </span>
                    </div>
                    <div v-else>
                        <span>{{ meta.promptId + 1 + '. ' }}</span>
                        <span
                            v-for="(word, widx) in meta.promptTokenDiff"
                            :key="'hbrecord-' + key + '-' + widx"
                            class="hover:bg-amber-200 cursor-pointer"
                            :class="[
                                'hb-word-' + word.action,
                            ]"
                            @mouseenter="emit('hover-word', {
                                action: word.action,
                                text: word.text
                            })"
                            @mouseleave="emit('hover-prompt', key)"
                        >
                            {{ word.text + ' ' }}
                        </span>
                    </div>
                    <div class="absolute right-0 bottom-0 m-1 flex space-x-1"
                        v-if="showCopyIcon[key]"
                    >
                        <img
                            :src="rawIcon"
                            v-if="!showRawPrompt[key]"
                            class="w-4 h-4 cursor-pointer"
                            @click="() => showRawPrompt[key] = true"
                        />
                        <img
                            v-if="showRawPrompt[key]"
                            :src="shrinkIcon"
                            class="w-4 h-4 cursor-pointer"
                            @click="() => showRawPrompt[key] = false"
                        />
                        <img
                            :src="copyIcon"
                            class="w-4 h-4 cursor-pointer"
                            @click="emit('copy-prompt', meta.prompt)"
                        />
                    </div>
                </div>
                <Transition>
                    <div class="relative p-1 text-neutral-600"
                        v-if="showRawPrompt[key]"
                    >
                        <div class="p-1 px-2 pr-4 border border-neutral-400 bg-neutral-50 rounded-sm text-xs font-mono">
                            {{ meta.prompt }}
                        </div>
                        <div class="absolute right-3 top-1 cursor-pointer p-0">
                            <span class="hover:font-bold"
                                @click="() => showRawPrompt[key] = false"
                            >&times;</span>
                        </div>
                    </div>
                </Transition>
                </div>
                <div class="hbrecord-prompt w-full px-2 py-1 grid grid-cols-4 gap-1 min-h-full place-items-center">
                    <div
                        v-for="(image, iidx) in details"
                        :key="image.id"
                        class="cursor-pointer p-1 rounded-sm hover:shadow-custom hover:bg-amber-200 col-span-1"
                        :class="{
                            'shadow-custom bg-amber-200': hoveredImage && hoveredImage.promptIndex === key && hoveredImage.imageId === image.id,
                        }"
                    >
                        <img
                            :src="'data:image/png;base64,' + image.data"
                            @click="emit('open-image', {
                                data: image.data,
                                filename: image.id,
                            })"
                            @mouseenter="emit('hover-image', {
                                promptIndex: key,
                                imageIndex: iidx,
                                imageId: image.id,
                            })"
                            @mouseleave="emit('unhover-image', null)"
                        />
                    </div>
                </div>
            </div>
            <VLoading v-if="cache" />
        </div>
    </div>
</template>

<style scoped>
.hb-word-r {
    color: rgb(241, 41, 41);
    text-decoration: line-through;
}

.hb-word-i {
    color: steelblue;
    font-weight: bold;
}

.hb-word-iw {
    color: steelblue;
}

.hb-word-rw {
    color: rgb(241, 41, 41);
}

.hb-word-m {
    color: mediumaquamarine;
}

.hover\:shadow-custom:hover {
  box-shadow: rgba(0, 0, 0, 0.2) 0px 3px 6px, rgba(0, 0, 0, 0.3) 0px 3px 6px;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.2s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
