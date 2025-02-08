<script lang="ts" setup>
import { ref, toRefs, watch } from 'vue'

const props = defineProps({
    attributeName: {
        type: String,
        required: true,
    },
    descriptionStart: {
        type: String,
        default: '',
    },
    descriptionEnd: {
        type: String,
        default: '',
    },
    defaultValue: {
        type: Number,
        default: 50,
    },
    fillBar: {
        type: Boolean,
        default: true,
    },
    rangeDirection: {
        type: String,
        default: 'lower'
    },
    leftValue: {
        type: Number,
        default: 0,
    },
    rightValue: {
        type: Number,
        default: 100,
    },
    precision: {
        type: Number,
        default: 0,
    },
})

const {
    attributeName,
    leftValue,
    precision
} = props

const {
    rightValue,
    defaultValue
} = toRefs(props)

const computeValue = (val: number) => {
    return parseFloat((leftValue + val * (rightValue.value - leftValue) / 100).toFixed(precision))
}
const reverseValue = (val: number) => {
    return (val - leftValue) / (rightValue.value - leftValue) * 100
}

const value = ref(reverseValue(defaultValue.value))
watch(defaultValue, () => {
    value.value = reverseValue(defaultValue.value)
})

const emit = defineEmits(['input', 'change'])
const formatTooltip = (val: number) => {
    const computedValue = computeValue(val)
    emit('input', computedValue)
    return computedValue
}
const handleChange = (val: number) => {
    emit('change', computeValue(val))
}
</script>

<template>
    <div class="flex items-center px-3">
        <span class="text-xs mr-1">{{ attributeName }}</span>
        <span class="text-xs mr-1" v-if="descriptionStart">{{ descriptionStart }}</span>
        <el-slider
            v-model="value"
            size="small"
            class="w-16 ml-2 h-1"
            :class="{
                'no-fill-bar': fillBar === false,
                'reverse-bar': rangeDirection === 'upper',
            }"
            :format-tooltip="formatTooltip"
            @change="handleChange"
        />
        <span class="text-xs ml-4" v-if="descriptionEnd">{{ descriptionEnd }}</span>
    </div>
</template>

<style>
.el-slider__runway {
    height: 0.25rem;
    background-color: #475569;
}

.el-slider__button {
    width: 0.75rem;
    height: 0.75rem;
    border-color: #94a3b8;
    border-width: 1px;
}

.el-slider__bar {
    height: 0.25rem;
    background-color: #e2e8f0;
}

.no-fill-bar .el-slider__bar {
    background-color: transparent;
}

.reverse-bar .el-slider__runway {
    background-color: #e2e8f0;
}
.reverse-bar .el-slider__bar {
    background-color: #475569;
}
</style>
