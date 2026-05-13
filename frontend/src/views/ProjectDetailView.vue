<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <!-- Loading -->
    <div v-if="loading" class="max-w-4xl mx-auto">
      <div class="h-4 w-32 skeleton mb-6"></div>
      <div class="h-64 sm:h-80 skeleton rounded-2xl mb-8"></div>
      <div class="glass rounded-2xl p-8 space-y-3">
        <div class="h-4 w-3/4 skeleton"></div>
        <div class="h-4 w-full skeleton"></div>
        <div class="h-4 w-5/6 skeleton"></div>
      </div>
    </div>
    <!-- Error -->
    <div v-else-if="error" class="max-w-4xl mx-auto text-center py-20">
      <p class="text-gray-500 dark:text-gray-400 text-lg mb-4">{{ error }}</p>
      <router-link to="/projects" class="text-primary-500 hover:text-primary-400">返回作品集</router-link>
    </div>
    <!-- Content -->
    <article v-else class="max-w-4xl mx-auto">
      <header class="mb-12">
        <router-link to="/projects" class="inline-flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors duration-200 mb-6">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          返回作品集
        </router-link>
        <div v-if="project.icon" class="h-64 sm:h-80 bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-2xl flex items-center justify-center mb-8">
          <span class="text-9xl">{{ project.icon }}</span>
        </div>
        <div v-if="project.status" class="flex items-center space-x-3 mb-4">
          <span class="px-3 py-1 text-sm bg-accent-500/20 text-accent-600 dark:text-accent-300 rounded-full">{{ project.status }}</span>
        </div>
        <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white">{{ project.name }}</h1>
        <p class="text-gray-500 dark:text-gray-400 text-lg mb-6">{{ project.description }}</p>
      </header>
      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">项目详情</h2>
        <p class="text-gray-600 dark:text-gray-300 leading-relaxed">{{ project.full_description }}</p>
      </div>
      <div v-if="project.features && project.features.length" class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">功能特性</h2>
        <ul class="space-y-3">
          <li v-for="feature in project.features" :key="feature" class="flex items-start text-gray-600 dark:text-gray-300">
            <svg class="w-5 h-5 text-primary-500 dark:text-primary-400 flex-shrink-0 mr-3 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" /></svg>
            {{ feature }}
          </li>
        </ul>
      </div>
      <div v-if="project.techs && project.techs.length" class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">技术栈</h2>
        <div class="flex flex-wrap gap-3">
          <span v-for="tech in project.techs" :key="tech" class="px-3 py-1 text-sm bg-gray-100 dark:bg-dark-50 text-gray-600 dark:text-gray-300 rounded-full">{{ tech }}</span>
        </div>
      </div>
      <div v-if="project.demo_url || project.repo_url" class="flex flex-col sm:flex-row gap-4">
        <a v-if="project.demo_url" :href="project.demo_url" target="_blank" class="px-6 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors">在线演示</a>
        <a v-if="project.repo_url" :href="project.repo_url" target="_blank" class="px-6 py-3 glass text-gray-700 dark:text-gray-300 rounded-xl hover:bg-white/10">源代码</a>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { projectApi } from '@/api'

const route = useRoute()

interface Project {
  id: number; name: string; description: string; full_description: string; icon: string | null; status: string; techs: string[]; features: string[]; demo_url: string | null; repo_url: string | null;
}

const project = ref<Project | null>(null)
const loading = ref(true)
const error = ref('')

async function fetchProject() {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id as string
    const res: any = await projectApi.getById(id)
    if (res.success && res.data) {
      project.value = res.data
    } else {
      error.value = '项目未找到'
    }
  } catch {
    error.value = '加载失败，请检查后端是否启动'
  } finally {
    loading.value = false
  }
}

onMounted(fetchProject)
</script>