<script lang="ts" setup>
import { storeToRefs } from 'pinia'
import { useStore as useSessionStore } from '@/stores/session'
import { useStore as useControlStore } from '@/stores/control'

import type { CacheRecord } from '@/plugins/session'

import VInput from './VInput.vue'
import TheViewSessionList from './TheViewSessionList.vue'

const sessionStore = useSessionStore()
const controlStore = useControlStore()

const { cache } = storeToRefs(sessionStore)
const { copiedPrompt } = storeToRefs(controlStore)

const handleRunGeneration = (inputValue: string) => {
    if (cache.value) {
        window.alert('Please wait for the current generation to finish')
        return
    }
    const payload: CacheRecord = {
        prompt: inputValue.trim(),
    }
    sessionStore.runGeneration(payload)
}
</script>

<template>
    <div class="bg-neutral-900 h-full flex flex-col">
        <div class="h-1/2">
            <Suspense>
                <TheViewSessionList />
            </Suspense>
        </div>
        <div class="h-1/2 p-2">
            <VInput class="h-full"
                :copied-text="copiedPrompt || undefined"
                @enter-input="handleRunGeneration"
            />
        </div>
    </div>
</template>