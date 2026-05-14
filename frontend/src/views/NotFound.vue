<template>
  <div class="min-h-[80vh] flex flex-col items-center justify-center text-center px-4">
    <h1 class="text-8xl font-bold text-primary-500/20 mb-4">404</h1>
    <h2 class="text-2xl font-semibold text-gray-800 dark:text-white mb-2">Page Not Found</h2>
    <p class="text-gray-500 dark:text-gray-400 mb-8">The page you are looking for doesn't exist or has been moved.</p>
    <router-link to="/" class="px-6 py-3 bg-primary-500 text-white font-medium rounded-xl hover:bg-primary-600 transition-colors">
      Return Home
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { useSEO } from '@/composables/useSEO'
useSEO({ title: '404 - Page Not Found' })
</script>
