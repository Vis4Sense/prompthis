<script setup lang="ts">
import TheTitle from './TheViewTitle.vue'
import TheControlPanel from './TheViewControls.vue'
import TheUser from './TheViewUser.vue'
</script>

<template>
    <div class="flex items-center justify-between bg-neutral-950 px-3 py-2">
        <TheTitle />
        <TheControlPanel />
        <TheUser />
    </div>
</template>