<script setup lang="ts">
import { onMounted } from 'vue';
import { RouterView } from 'vue-router'

const baseSize = 16;

const setRem = () => {
  let width = window.innerWidth;
  let height = window.innerHeight;
  const scale = Math.max(width, height) / 1280;
  let rem = baseSize * Math.min(scale, 2);
  rem = Math.min(rem, 20);
  document.documentElement.style.fontSize = rem + "px";
}

onMounted(() => {
  setRem();
  window.addEventListener("resize", setRem);
  document.title = "PrompTHis";
})

</script>

<template>
  <RouterView />
</template>
