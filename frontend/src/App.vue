<template>
    <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN">
        <n-message-provider>
            <n-notification-provider>
                <n-dialog-provider>
                    <AppLayout />
                </n-dialog-provider>
            </n-notification-provider>
        </n-message-provider>
    </n-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
    NConfigProvider,
    NMessageProvider,
    NNotificationProvider,
    NDialogProvider,
    zhCN,
    dateZhCN,
    darkTheme,
} from 'naive-ui'
import AppLayout from '@/components/AppLayout.vue'

// Optional: dark mode toggle (default light)
const theme = ref<typeof darkTheme | null>(null)
</script>
