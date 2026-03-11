<template>
    <div class="app-shell">
        <!-- Top navigation -->
        <header class="app-header">
            <div class="header-inner">
                <router-link to="/" class="brand">
                    <span class="brand-icon">⚡</span>
                    <span class="brand-name">后真相时代</span>
                </router-link>
                <div class="header-center">
                    <SearchBar compact @search="handleSearch" />
                </div>
                <nav class="header-nav">
                    <router-link to="/" class="nav-link">首页</router-link>
                    <router-link to="/admin" class="nav-link">管理</router-link>
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
import { useRouter } from 'vue-router'
import SearchBar from './SearchBar.vue'

const router = useRouter()

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
    background: #fff;
}

/* ── Header ── */
.app-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #fff;
    border-bottom: 1px solid #e5e7eb;
}

.header-inner {
    max-width: 960px;
    margin: 0 auto;
    padding: 0 24px;
    height: 56px;
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
}

.brand-name {
    font-size: 18px;
    font-weight: 800;
    color: #1a1a1a;
    letter-spacing: -0.02em;
}

/* Center search */
.header-center {
    flex: 1;
    max-width: 400px;
}

/* Nav */
.header-nav {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
}

.nav-link {
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    color: #6b7280;
    text-decoration: none;
    transition: all 0.15s;
}

.nav-link:hover {
    background: #f3f4f6;
    color: #1a1a1a;
}

.nav-link.router-link-active {
    color: #ef4444;
    font-weight: 600;
}

/* ── Main ── */
.app-main {
    flex: 1;
}

.main-inner {
    max-width: 960px;
    margin: 0 auto;
    padding: 24px 24px;
}

/* ── Footer ── */
.app-footer {
    background: #fafafa;
    border-top: 1px solid #f3f4f6;
    padding: 14px 24px;
}

.footer-inner {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 12px;
    color: #9ca3af;
}

.footer-brand {
    color: #ef4444;
    font-weight: 600;
}

.footer-divider {
    color: #d1d5db;
}

@media (max-width: 640px) {
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
