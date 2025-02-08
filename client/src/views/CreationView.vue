<script setup lang="ts">
import { ref, onBeforeMount } from 'vue';

import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from 'vue-router';

import { storeToRefs } from 'pinia'
import { useStore as useUserStore } from '@/stores/user'
import { useStore as useControlStore } from '@/stores/control'

import TheViewHeader from '../components/TheViewHeader.vue'
import ThePanelCreate from '../components/ThePanelCreate.vue'
import ThePanelVis from '../components/ThePanelVis.vue'
import VFullImage from '@/components/VFullImage.vue'


const route = useRoute()
const userStore = useUserStore()
const controlStore = useControlStore()

const createPanelRef = ref<HTMLDivElement>()
const render = ref(false)

const { fullImageModal, fullImageData } = storeToRefs(controlStore)

onBeforeMount(async () => {
    const queryParams = route.query
    const userName = queryParams.username as string
    const userId = queryParams.userid as string
    const sessionId = queryParams.sessionid as string
    if (userName && userName !== userStore.userName) {
        await userStore.userLogIn(userName)
    } else if (userId !== undefined && parseInt(userId) !== userStore.userId) {
        // user id is not allowed
        alert('Invalid url. Please log in from the home page.')
        return
    }
    if (sessionId !== undefined && parseInt(sessionId) !== userStore.sessionId) {
        userStore.setSessionId(parseInt(sessionId))
    }
    render.value = true
})
onBeforeRouteUpdate(async (to, from) => {
    const queryParamsTo = to.query
    const queryParamsFr = from.query
    const userNameTo = queryParamsTo.username as string
    const userIdTo = queryParamsTo.userid as string
    const sessionIdTo = queryParamsTo.sessionid as string
    const userNameFr = queryParamsFr.username as string
    const userIdFr = queryParamsFr.userid as string
    const sessionIdFr = queryParamsFr.sessionid as string
    // if user changes
    if (userNameTo && userNameTo !== userNameFr) {
        await userStore.userLogIn(userNameTo)
    } else if (userIdTo !== undefined && userIdTo !== userIdFr) {
        userStore.userLogInById(parseInt(userIdTo))
    }
    // if session changes
    if (sessionIdTo !== undefined && sessionIdTo !== sessionIdFr) {
        userStore.setSessionId(parseInt(sessionIdTo))
    }
    render.value = true
})
onBeforeRouteLeave((to, from) => {
    if (to.name === 'home') {
        render.value = false
        userStore.emptyStore()
    }
})
</script>

<template>
    <div class="h-screen w-full flex flex-col">
        <TheViewHeader />
        <div class="flex-auto overflow-auto flex" v-if="render">
            <ThePanelCreate class="min-w-50 w-15/100"
                ref="createPanelRef"
            />
            <Suspense>
                <ThePanelVis class="flex-1"
                    @open-image="controlStore.openFullImage($event)"
                />
            </Suspense>
        </div>
        <VFullImage
            :modal-open="fullImageModal"
            :image-data="fullImageData"
            @close-image="controlStore.closeFullImage()"
        />
    </div>
</template>
