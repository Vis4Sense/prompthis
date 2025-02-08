<script setup lang="ts">
import TheTitle from '../components/TheViewTitle.vue'
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useStore as useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const scrollToSection = (hash: string) => {
  const element = document.querySelector(hash);
  if (element) {
    const yOffset = element.getBoundingClientRect().top;
    window.scrollTo({ top: yOffset, behavior: 'smooth' });
  }
}

onMounted(() => {
  if (route.hash) {
    scrollToSection(route.hash);
  }
});

router.afterEach((to, from) => {
  if (to.path === '/') {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  if (to.hash) {
    scrollToSection(to.hash);
  }
});

const username = ref('');

const login = async () => {
  const usernameVal = username.value.trim();
  if (usernameVal) {
    const { status } = await userStore.userLogIn(usernameVal)
    if (status === 'success') {
        router.push({
            path: '/create',
            query: { username: usernameVal }
        })
    } else {
        window.alert('Username does not exist')
    }
  } else {
    window.alert('Please enter a username')
  }
};

const loginAsGuest = async () => {
  const usernameVal = window.crypto.randomUUID();
  const { status } = await userStore.userLogIn(usernameVal)
  if (status === 'success') {
      router.push({
          path: '/create',
          query: { username: usernameVal }
      })
  } else {
      window.alert('Failed to log in as guest, please try again!')
  }
};
</script>

<template>
  <div class="h-screen w-screen flex flex-col">
    <header>
      <nav class="flex items-center justify-center fixed w-full bg-gradient-to-b from-white">
        <div class="container md flex justify-between items-center w-full py-6 px-4">
          <router-link to="/">
            <div class="flex">
              <img class="h-28px pr-2" src="/favicon.ico">
              <span class="text-lg font-medium">
                PrompTHis
              </span>
            </div>
          </router-link>
          <div class="flex space-x-6 text-base">
            <router-link to="#about">About</router-link>
            <router-link to="#gallery">Gallery</router-link>
            <router-link to="#create">Create</router-link>
            <a href="https://arxiv.org/abs/2403.09615">Paper</a>
          </div>
        </div>
      </nav>
    </header>
    <main class="w-full flex flex-col items-center">
      <div class="container md flex flex-col space-y-8 px-4">
        <div class="text-4xl pt-24 pb-4 text-center">
          Prompt History for Text-to-Image Generation
        </div>

        <!-- About -->
        <div id="about" class="flex justify-center">
          <iframe src="https://drive.google.com/file/d/1HUE_79QyuAcuB_UPbSN4QGfC5l8aITLM/preview" class="w-160 h-90" allow="autoplay" allowfullscreen></iframe>
        </div>

        <!-- Gallery -->
        <div id="gallery" class="px-4">
          <div class="text-2xl font-medium mb-4">
            Explore pre-recorded sessions
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div class="aspect-w-16 aspect-h-9 shadow hover:shadow-lg">
              <router-link to="/view?userid=0&sessionid=1">
              <img src="../assets/thumbnails/u21-s1.png" class="object-cover">
              </router-link>
            </div>
            <div class="aspect-w-16 aspect-h-9 shadow hover:shadow-lg">
              <router-link to="/view?userid=0&sessionid=2">
              <img src="../assets/thumbnails/u21-s2.png" class="object-cover">
              </router-link>
            </div>
          </div>
        </div>

        <!-- Create -->
        <div id="create" class="px-4">
          <div class="text-2xl font-medium mb-4">
            Create your own sessions with PrompTHis
          </div>
          <div class="text-lg mt-6">
            <div class="grid grid-cols-2 gap-16 px-16">
              <div class="border border-t-2 border-t-gray px-10 py-6 flex flex-col items-center hover:bg-gray-100/40">
                <span class="text-xl">Guest Mode</span>
                <form class="mt-4" @submit.prevent="loginAsGuest">
                  <button
                    class="px-4 py-1 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200">
                    Quick start
                  </button>
                </form>
              </div>
              <div class="border border-t-2 border-t-gray px-10 py-6 flex flex-col items-center hover:bg-gray-100/40">
                <span class="text-xl">User Mode</span>
                <form class="flex space-x-4 text-neutral-800 mt-4" @submit.prevent="login">
                    <input type="text" v-model="username" placeholder="Enter any username"
                        class="px-2 py-1 border border-gray-300 rounded-lg focus:outline-none focus:border-gray-500 w-50" />
                    <button
                      class="px-4 py-1 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200">
                        Log in
                    </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-8 py-2 bg-gray-600 w-full text-neutral-300 text-center">
        <div class="text-sm">PrompTHis: Visualizing the Process and Influence of Prompt Editing during Text-to-Image Creation</div>
        <div class="text-[0.7rem]">Peking University, University of Nottingham &copy; 2024</div>
      </div>
    </main>
  </div>
</template>
