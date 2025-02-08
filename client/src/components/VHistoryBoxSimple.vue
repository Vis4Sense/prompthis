<script lang="ts" setup>
import { watch, ref, toRefs, nextTick, onMounted } from 'vue'
import type { PropType } from 'vue'

import { storeToRefs } from 'pinia'
import { useStore as useSessionStore } from '@/stores/session'

import VRecord from './VRecord.vue'
import VLoading from './VLoading.vue'

const props = defineProps({
    records: {
        type: Array as PropType<Record<string, any>[]>,
        required: true,
    },
})

const {
    records
} = toRefs(props)

const recordContainer = ref<HTMLDivElement>()

const sessionStore = useSessionStore()
const { cache } = storeToRefs(sessionStore)

const scrollToBottom = () => {
    if (recordContainer.value) {
        recordContainer.value.scrollTop = recordContainer.value.scrollHeight
    }
}

watch(records, () => {
    nextTick(scrollToBottom)
})

onMounted(() => {
    nextTick(scrollToBottom)
})

const emit = defineEmits(['open-image'])
</script>

<template>
    <div class="w-full h-full border-l-1 border-r-1 border-neutral-400 py-2 ">
        <div class="h-full overflow-y-auto smooth-scroll" ref="recordContainer">
            <VRecord v-for="({ meta, details }, key) in records" :key="key" :meta="meta" :details="details"
                @open-image="emit('open-image', $event)"
            />
            <VLoading v-if="cache" />
        </div>
    </div>
</template>

<style scoped>
.smooth-scroll {
    scroll-behavior: smooth;
}
</style>
