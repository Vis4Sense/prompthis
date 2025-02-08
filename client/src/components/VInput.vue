<script lang="ts" setup>
import { ref, toRefs, defineEmits, watch } from 'vue'
import helpIcon from '@/assets/icons/help.svg'

const props = defineProps({
    placeholderText: {
        type: String,
        default: 'Enter your prompt...',
    },
    copiedText: {
        type: String,
        default: null,
    }
})

const {
    copiedText
} = toRefs(props)

const inputValue = ref('')

const emit = defineEmits(['enterInput'])

const handleInput = () => {
    emit('enterInput', inputValue.value)
    setTimeout(() => {
        inputValue.value = ''
    }, 0);
}

watch(copiedText, (newVal) => {
    if (newVal) {
        addCopiedText(newVal)
    }
})

const addCopiedText = (text) => {
    if (inputValue.value.length === 0) {
        inputValue.value = text
    } else if (inputValue.value.endsWith(' ')) {
        inputValue.value += text
    } else {
        inputValue.value += ' ' + text
    }
}
</script>

<template>
    <div class="text-neutral-50 flex flex-col">
        <span>Create</span>
        <div class="flex-auto">
            <textarea ref="textareaRef" type="text" class="bg-neutral-700 p-1 w-full h-full focus:outline-none"
                v-model="inputValue" :placeholder="placeholderText" @keydown.enter="handleInput" />
        </div>
        <div class="input-cheat-sheet mt-2">
            <div class="input-cheat-sheet-title flex text-neutral-200">
                <img :src="helpIcon" width="16" alt="help" />
                <span class="text-xs px-1">Stable Diffusion Prompt</span>
            </div>
            <div class="input-cheat-sheet-content text-neutral-400">
                <div class="input-cheat-sheet-content-item">
                    <span class="text-xs">(phrase)</span>
                    <span class="text-xs text-neutral-500">-&gt;</span>
                    <span class="text-xs">weight * 1.1</span>
                </div>
                <div class="input-cheat-sheet-content-item">
                    <span class="text-xs">((phrase))</span>
                    <span class="text-xs text-neutral-500">-&gt;</span>
                    <span class="text-xs">weight * 1.1 * 1.1</span>
                </div>
                <div class="input-cheat-sheet-content-item">
                    <span class="text-xs">[phrase]</span>
                    <span class="text-xs text-neutral-500">-&gt;</span>
                    <span class="text-xs">weight / 1.1</span>
                </div>
                <div class="input-cheat-sheet-content-item">
                    <span class="text-xs">[[phrase]]</span>
                    <span class="text-xs text-neutral-500">-&gt;</span>
                    <span class="text-xs">weight / (1.1 * 1.1)</span>
                </div>
            </div>
            <div class="input-cheat-sheet-example">
                <div class="input-cheat-sheet-example-item">
                    <span class="text-xs text-neutral-200">Example: </span>
                    <span class="text-xs text-neutral-400">penguin holding a (beer)</span>
                </div>
            </div>
        </div>
    </div>
</template>
