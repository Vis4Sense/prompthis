<script lang="ts" setup>

const {
    description
} = defineProps({
    description: {
        type: String,
        default: "",
    }
})

</script>

<template>
    <div class="p-2 cursor-pointer text-neutral-300">
        <div class="border border-gray-500 rounded-md flex flex-row items-center box">
            <div class="flex justify-center items-center icon-add px-2">
                <p class="text-lg">+</p>
            </div>
            <div class="flex items-center flex-auto">
                <p class="text-sm">{{ description }}</p>
            </div>
        </div>
    </div>
</template>
