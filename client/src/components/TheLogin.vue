<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

import { useStore as useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

const username = ref('');

const login = async () => {
    if (username.value) {
        const { status } = await userStore.userLogIn(username.value)
        if (status === 'success') {
            router.push({
                path: '/create',
                query: { username: username.value }
            })
        } else {
            window.alert('Username does not exist')
        }
    }
};
</script>

<template>
    <div class="flex justify-center items-center">
        <form class="flex space-x-4 text-neutral-800" @submit.prevent="login">
            <input type="text" v-model="username" placeholder="Enter your username"
                class="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500" />
            <button
                class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:bg-blue-600">
                Log in
            </button>
        </form>
    </div>
</template>
