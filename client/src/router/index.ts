import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/PublicView.vue')
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue')
    },
    {
      path: '/create',
      name: 'create',
      component: () => import('../views/CreationView.vue')
    },
    {
      path: '/view',
      name: 'explore',
      component: () => import('../views/ExploreView.vue')
    },
    {
      path: '/vinternal',
      name: 'internal',
      component: HomeView
    },
  ]
})

export default router
