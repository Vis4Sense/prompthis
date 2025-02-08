<script setup lang="ts">
import TheTitle from '../components/TheViewTitle.vue'
import TheWelcome from '../components/TheWelcome.vue'
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-neutral-800">
    <header class="flex justify-center items-center w-full py-6 px-4">
      <div class="container md">
        <TheTitle />
      </div>
    </header>
    <main class="flex-auto">
      <TheWelcome />
    </main>
  </div>
</template>
