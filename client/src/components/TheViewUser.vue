<script lang="ts" setup>
import { storeToRefs } from 'pinia';
import { useStore as useUserStore } from '@/stores/user';

const userStore = useUserStore();
const { userName } = storeToRefs(userStore);
</script>

<template>
    <span class="text-sm text-slate-50">User</span>
</template>