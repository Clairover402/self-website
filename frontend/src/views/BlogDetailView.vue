<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <!-- Loading -->
    <div v-if="loading" class="max-w-4xl mx-auto">
      <div class="text-center mb-12">
        <div class="h-8 w-48 skeleton mx-auto mb-4"></div>
        <div class="h-4 w-32 skeleton mx-auto"></div>
      </div>
      <div class="glass rounded-2xl p-8 sm:p-12">
        <div class="space-y-3"><div class="h-4 w-full skeleton"></div><div class="h-4 w-5/6 skeleton"></div><div class="h-4 w-3/4 skeleton"></div><div class="h-4 w-full skeleton"></div></div>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="max-w-4xl mx-auto text-center py-20">
      <p class="text-gray-500 dark:text-gray-400 text-lg mb-4">{{ error }}</p>
      <router-link to="/blog" class="text-primary-500 hover:text-primary-400">返回博客列表</router-link>
    </div>

    <!-- Content -->
    <article v-else class="max-w-4xl mx-auto">
      <header class="mb-12 text-center">
        <div class="flex items-center justify-center space-x-2 mb-4">
          <span v-for="tag in post.tags" :key="tag" class="px-3 py-1 text-sm bg-primary-500/20 text-primary-600 dark:text-primary-300 rounded-full">{{ tag }}</span>
        </div>
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">{{ post.title }}</h1>
        <div class="flex items-center justify-center space-x-6 text-gray-500 dark:text-gray-400 text-sm">
          <span>{{ formatDate(post.created_at) }}</span>
          <span>{{ post.read_time }} 分钟阅读</span>
        </div>
      </header>
      <div class="glass rounded-2xl p-8 sm:p-12">
        <div class="prose dark:prose-invert prose-lg max-w-none" v-html="renderedContent"></div>
      </div>
      <div class="mt-12 flex justify-between items-center">
        <router-link to="/blog" class="flex items-center text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors duration-200">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg>
          返回博客
        </router-link>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { blogApi } from '@/api'
import { marked } from 'marked'

const route = useRoute()

interface Blog {
  id: number; title: string; slug: string; excerpt: string; content: string; cover: string | null; tags: string[]; read_time: number; created_at: string; updated_at: string;
}

const post = ref<Blog | null>(null)
const loading = ref(true)
const error = ref('')

const renderedContent = computed(() => {
  if (!post.value) return ''
  return marked(post.value.content)
})

function formatDate(d: string) {
  return new Date(d).toISOString().slice(0, 10)
}

async function fetchBlog() {
  loading.value = true
  error.value = ''
  try {
    const slug = route.params.slug as string
    const res: any = await blogApi.getBySlug(slug)
    if (res.success && res.data) {
      post.value = res.data
    } else {
      error.value = '文章未找到'
    }
  } catch {
    error.value = '加载失败，请检查后端是否启动'
  } finally {
    loading.value = false
  }
}

onMounted(fetchBlog)
</script>