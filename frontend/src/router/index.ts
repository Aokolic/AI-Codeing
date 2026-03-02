import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { hasToken } from '@/api/client'

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        name: 'Home',
        component: () => import('@/pages/HomePage.vue'),
        meta: { title: '热点案件' },
    },
    {
        path: '/cases/:id',
        name: 'CaseDetail',
        component: () => import('@/pages/CaseDetailPage.vue'),
        meta: { title: '案件时间线' },
    },
    {
        path: '/search',
        name: 'Search',
        component: () => import('@/pages/SearchResultPage.vue'),
        meta: { title: '搜索结果' },
    },
    {
        path: '/admin',
        name: 'Admin',
        component: () => import('@/pages/AdminPage.vue'),
        meta: { title: '管理后台', requiresAuth: true },
    },
    {
        path: '/:pathMatch(.*)*',
        redirect: '/',
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
})

// Auth guard
router.beforeEach((to, _from, next) => {
    if (to.meta.requiresAuth && !hasToken()) {
        next({ name: 'Home', query: { redirect: to.fullPath } })
    } else {
        document.title = `${to.meta.title as string} — 后真相时代`
        next()
    }
})

export default router
