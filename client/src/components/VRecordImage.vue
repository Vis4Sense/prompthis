<script lang="ts" setup>
import type { PropType } from 'vue';

const {
    images,
} = defineProps({
    images: {
        type: Array as PropType<Record<string, any>[]>,
        required: true,
    },
})

const emit = defineEmits(['open-image'])
</script>

<template>
    <div class="flex w-full px-2 py-1">
        <div v-for="image in images" :key="image.id" class="md:w-1/4 p-2 cursor-pointer">
            <img
                :src="'data:image/jpeg;base64,' + image.data"
                @click="emit('open-image', image.data)"
            />
        </div>
    </div>
</template>