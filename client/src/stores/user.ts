import { acceptHMRUpdate, defineStore } from 'pinia'

import { urls } from '../plugins/apis'
import { request } from '../utils/request'

import type { SessionItem as Session } from '../plugins/session'
import type { LogInResponse, CreateSessionResponse } from '../plugins/apis'

import { transformRawSessionList } from '../plugins/session'

export const useStore = defineStore('user', {
    state: () => ({
        userId: null as number | null,
        userName: null as string | null,
        sessionId: null as number | null,
        sessions: [] as Session[]
    }),
    getters: {
    },
    actions: {
        async userLogIn(username: string) {
            /** send username to backend for verification */
            const payload = { username }
            const data = await request<LogInResponse>(urls.logIn, payload)
            const { status, userId } = data
            if (status === 'success') {
                this.setUserId(userId)
                this.setUserName(username)
            }
            return data
        },
        userLogInById(userId: number) {
            this.setUserId(userId)
            this.setUserName('user' + userId)
        },
        async createSession() {
            const payload = { userId: this.userId }
            const data = await request<CreateSessionResponse>(urls.createSession, payload)
            const sessions = data.sessions as Session[]
            this.updateSessions(sessions)
            this.setSessionIdtoLatest()
        },
        async fetchSessions() {
            const payload = { userId: this.userId }
            const data = await request<CreateSessionResponse>(urls.fetchSessionList, payload)
            const sessions = data.sessions as Session[]
            this.updateSessions(sessions)

            if (this.sessions.length === 0) {
                await this.createSession()
            }
        },
        setUserId(userId: number) {
            this.userId = userId
        },
        setUserName(username: string) {
            this.userName = username
        },
        updateSessions(sessions: Session[]) {
            const sessions_ = transformRawSessionList(sessions) as Session[]
            this.sessions = sessions_.sort((a, b) => b.sessionId - a.sessionId)
            if (this.sessionId === null) this.setSessionIdtoLatest()
        },
        setSessionId(sessionId: number) {
            this.sessionId = sessionId
        },
        setSessionIdtoLatest() {
            if (this.sessions.length === 0) return
            const latestSession = this.sessions[0]
            this.sessionId = latestSession.sessionId
        },
        emptyStore() {
            this.userId = null
            this.userName = null
            this.sessionId = null
            this.sessions = []
        }
    }
})

if (import.meta.hot) {
    import.meta.hot.accept(acceptHMRUpdate(useStore, import.meta.hot))
}