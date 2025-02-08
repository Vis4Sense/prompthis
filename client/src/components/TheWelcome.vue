<script lang="ts" setup>
import TheLogin from '../components/TheLogin.vue'
</script>

<template>
  <div class="flex justify-center items-center w-full">
    <div class="w-7/10 min-w-260 p-20">
      <div class="text-center text-neutral-200">
        <div class="text-6xl font-bold py-8">PrompTHis(tory)</div>
      </div>

      <!-- log in -->
      <div class="flex justify-center items-center py-20">
        <TheLogin />
      </div>
    </div>
  </div>
</template>
