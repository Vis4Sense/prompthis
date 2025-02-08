<script lang="ts" setup>
import VNewSession from './VNewSession.vue';

import { storeToRefs } from 'pinia';
import { useStore as useUserStore } from '@/stores/user'

const userStore = useUserStore()
await userStore.fetchSessions()

const { sessions, sessionId } = storeToRefs(userStore)

const handleCreateSession = () => {
    userStore.createSession()
}

const handleSelectSession = (id: number) => {
    userStore.setSessionId(id)
}
</script>

<template>
    <div class="h-full flex flex-col">
        <VNewSession description="New Session" @click="handleCreateSession" />
        <div class="p-2 text-neutral-300 h-full flex-auto overflow-y-auto">
            <div class="px-2 py-1 rounded-md cursor-pointer hover:bg-neutral-600"
                v-for="session in sessions"
                :key="session.sessionId"
                :class="{
                    'bg-neutral-700': session.sessionId === sessionId,
                }"
                @click="handleSelectSession(session.sessionId)"
            >
                <div>{{ session.sessionName }}</div>
            </div>
        </div>
    </div>
</template>