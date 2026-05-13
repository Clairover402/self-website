<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">作品集</h1>
        <p class="text-gray-600 dark:text-gray-400 text-lg">创新与实践的结晶</p>
      </div>
      <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div v-for="n in 4" :key="n" class="glass rounded-2xl overflow-hidden">
          <div class="h-64 skeleton"></div>
          <div class="p-6 space-y-3">
            <div class="h-6 w-1/3 skeleton"></div>
            <div class="h-4 w-full skeleton"></div>
            <div class="h-4 w-3/4 skeleton"></div>
            <div class="flex gap-2"><div class="h-6 w-16 skeleton"></div><div class="h-6 w-20 skeleton"></div><div class="h-6 w-14 skeleton"></div></div>
          </div>
        </div>
      </div>
      <div v-else-if="error" class="text-center py-20">
        <p class="text-gray-600 dark:text-gray-400 text-lg mb-4">{{ error }}</p>
        <button @click="fetchProjects" class="px-6 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors">重试</button>
      </div>
      <div v-else-if="projects.length === 0" class="text-center py-20"><p class="text-gray-600 dark:text-gray-500 text-lg">暂无项目</p></div>
      <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <article v-for="(project, index) in projects" :key="project.id" class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer" :style="{ animationDelay: `${index * 100}ms` }" @click="$router.push(`/projects/${project.id}`)">
          <div class="h-64 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center relative overflow-hidden">
            <span class="text-8xl group-hover:scale-110 transition-transform duration-500">{{ project.icon || "🚀" }}</span>
            <div class="absolute inset-0 bg-gradient-to-t from-black/40 dark:from-dark-100/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-6">
              <span class="px-6 py-2 bg-primary-500 text-white text-sm rounded-full">查看详情</span>
            </div>
          </div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-primary-400 transition-colors duration-200">{{ project.name }}</h3>
              <span class="px-3 py-1 text-xs bg-accent-500/20 text-accent-600 dark:text-accent-300 rounded-full">{{ project.status }}</span>
            </div>
            <p class="text-gray-600 dark:text-gray-400 text-sm mb-4">{{ project.description }}</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="tech in project.techs" :key="tech" class="px-3 py-1 text-xs bg-gray-100 dark:bg-dark-50 text-gray-700 dark:text-gray-300 rounded-full">{{ tech }}</span>
            </div>
          </div>
        </article>
      </div>
      <div v-if="!loading && !error && totalPages > 1" class="mt-12 flex justify-center items-center space-x-2">
        <button @click="goToPage(page - 1)" :disabled="page <= 1" class="px-4 py-2 glass rounded-lg text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors">上一页</button>
        <span class="text-gray-600 dark:text-gray-400 text-sm">{{ page }} / {{ totalPages }}</span>
        <button @click="goToPage(page + 1)" :disabled="page >= totalPages" class="px-4 py-2 glass rounded-lg text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { projectApi } from '@/api'
import { useSEO } from '@/composables/useSEO'

interface Project {
  id: number
  name: string
  description: string
  icon: string | null
  status: string
  techs: string[]
}

const projects = ref<Project[]>([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(1)

async function fetchProjects() {
  loading.value = true
  error.value = ''
  try {
    const res: any = await projectApi.getList({ page: page.value, page_size: 6 })
    if (res.success && res.data) {
      projects.value = res.data.items
      totalPages.value = res.data.total_pages
    } else {
      error.value = '加载失败'
    }
  } catch (e) {
    error.value = '网络错误，请检查后端是否启动'
  } finally {
    loading.value = false
  }
}

function goToPage(p: number) {
  page.value = p
  fetchProjects()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  useSEO({ title: '作品集', description: '创新与实践的结晶' })
  fetchProjects()
})
</script>

