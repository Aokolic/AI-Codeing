<template>
    <div class="app-shell">
        <!-- Top navigation -->
        <header class="app-header">
            <div class="header-inner">
                <router-link to="/" class="brand">
                    <span class="brand-icon">⚡</span>
                    <span class="brand-name">后真相时代</span>
                    <span class="brand-sub">信息甄别平台</span>
                </router-link>
                <div class="header-center">
                    <SearchBar compact @search="handleSearch" />
                </div>
                <nav class="header-nav">
                    <router-link to="/" class="nav-link">首页</router-link>
                    <router-link v-if="isAdmin" to="/admin" class="nav-link nav-admin">管理后台</router-link>
                    <router-link v-else to="/admin" class="nav-link nav-login">登录</router-link>
                </nav>
            </div>
        </header>

        <!-- Page content -->
        <main class="app-main">
            <div class="main-inner">
                <router-view />
            </div>
        </main>

        <!-- Footer -->
        <footer class="app-footer">
            <div class="footer-inner">
                <span class="footer-brand">⚡ 后真相时代</span>
                <span class="footer-divider">·</span>
                <span>信息甄别 · 时间线追踪 · 多源核实</span>
                <span class="footer-divider">·</span>
                <span>© 2026</span>
            </div>
        </footer>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { hasToken } from '@/api/client'
import SearchBar from './SearchBar.vue'

const router = useRouter()
const isAdmin = computed(() => hasToken())

function handleSearch(q: string) {
    router.push({ name: 'Search', query: { q } })
}
</script>

<style scoped>
/* ── Shell ── */
.app-shell {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #f0f2f7;
}

/* ── Header ── */
.app-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 60%, #312e81 100%);
    box-shadow: 0 2px 16px rgba(15, 23, 42, .35);
    backdrop-filter: blur(8px);
}

.header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px;
    height: 60px;
    display: flex;
    align-items: center;
    gap: 20px;
}

/* Brand */
.brand {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    flex-shrink: 0;
}

.brand-icon {
    font-size: 20px;
    filter: drop-shadow(0 0 6px #a5b4fc);
}

.brand-name {
    font-size: 17px;
    font-weight: 700;
    color: #e0e7ff;
    letter-spacing: -0.01em;
}

.brand-sub {
    font-size: 11px;
    color: #818cf8;
    background: rgba(129, 140, 248, .15);
    border: 1px solid rgba(129, 140, 248, .25);
    padding: 1px 7px;
    border-radius: 999px;
    letter-spacing: 0.04em;
}

/* Center search */
.header-center {
    flex: 1;
    max-width: 440px;
}

/* Nav */
.header-nav {
    display: flex;
    align-items: center;
    gap: 4px;
    flex-shrink: 0;
}

.nav-link {
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: #c7d2fe;
    text-decoration: none;
    transition: all 0.15s;
}

.nav-link:hover {
    background: rgba(255, 255, 255, .1);
    color: #fff;
}

.nav-link.router-link-active {
    background: rgba(99, 102, 241, .3);
    color: #e0e7ff;
}

.nav-admin {
    background: rgba(245, 158, 11, .15);
    border: 1px solid rgba(245, 158, 11, .3);
    color: #fcd34d;
}

.nav-admin:hover {
    background: rgba(245, 158, 11, .25);
    color: #fde68a;
}

.nav-login {
    border: 1px solid rgba(129, 140, 248, .3);
}

/* ── Main ── */
.app-main {
    flex: 1;
}

.main-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 28px 24px;
}

/* ── Footer ── */
.app-footer {
    background: #0f172a;
    border-top: 1px solid rgba(255, 255, 255, .06);
    padding: 14px 24px;
}

.footer-inner {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    color: #64748b;
}

.footer-brand {
    color: #818cf8;
    font-weight: 600;
}

.footer-divider {
    color: #334155;
}

@media (max-width: 640px) {

    .brand-sub,
    .header-center {
        display: none;
    }

    .header-inner {
        padding: 0 16px;
    }

    .main-inner {
        padding: 16px 16px;
    }
}
</style>
