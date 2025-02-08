<script lang="ts" setup>
import VRecordPrompt from './VRecordPrompt.vue'
import VRecordImage from './VRecordImage.vue'

const {
    meta,
    details
} = defineProps({
    meta: {
        type: Object,
        required: true,
    },
    details: {
        type: Array,
        default: null
    }
})

const emit = defineEmits(['open-image'])
</script>

<template>
    <div>
        <VRecordPrompt :data="meta" />
        <VRecordImage
            :images="details"
            @open-image="emit('open-image', $event)"
        />
    </div>
</template>