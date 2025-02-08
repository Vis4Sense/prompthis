<script lang="ts" setup>
const {
    data
} = defineProps({
    data: {
        type: Object,
        required: true
    }
})
</script>

<template>
    <div class="px-2 py-1">
        <div class="text-sm text-neutral-900">
            <span>{{ data.promptId + 1 + '. ' }}</span>
            <span>{{ data.prompt }}</span>
        </div>
    </div>
</template>