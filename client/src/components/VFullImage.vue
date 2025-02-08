<script lang="ts" setup>
import { toRefs } from 'vue'

const props = defineProps({
    modalOpen: {
        type: Boolean,
        required: true,
    },
    imageData: {
        type: String,
        default: null,
    },
})

const {
    modalOpen,
    imageData
} = toRefs(props)

const emit = defineEmits(['close-image'])
</script>

<template>
    <Transition name="fade">
        <div v-if="modalOpen" class="modal"
            @click.self="emit('close-image')"
        >
            <span class="close"
                @click="emit('close-image')"
            >&times;</span>
            <img
                v-if="imageData"
                :src="'data:image/png;base64,' + imageData"
                alt="Full Image"
            />
        </div>
    </Transition>
</template>

<style scoped>
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.8);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2;
}

.close {
    position: absolute;
    top: 20px;
    right: 20px;
    color: white;
    font-size: 24px;
    cursor: pointer;
}

.fade-enter-active,
.fade-leave-active
{
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
