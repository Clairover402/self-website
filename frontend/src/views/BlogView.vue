<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">技术博客</h1>
        <p class="text-gray-500 dark:text-gray-400 text-lg">分享技术见解与实践经验</p>
      </div>
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="n in 6" :key="n" class="glass rounded-2xl overflow-hidden">
          <div class="h-48 skeleton"></div>
          <div class="p-6 space-y-3"><div class="h-4 w-20 skeleton"></div><div class="h-6 w-3/4 skeleton"></div><div class="h-4 w-full skeleton"></div><div class="h-4 w-1/2 skeleton"></div></div>
        </div>
      </div>
      <div v-else-if="error" class="text-center py-20">
        <p class="text-gray-500 dark:text-gray-400 text-lg mb-4">{{ error }}</p>
        <button @click="fetchBlogs" class="px-6 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors">重试</button>
      </div>
      <div v-else-if="posts.length === 0" class="text-center py-20"><p class="text-gray-400 dark:text-gray-500 text-lg">暂无文章</p></div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <article v-for="(post, index) in posts" :key="post.slug" class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer" :style="{ animationDelay: `${index * 100}ms` }" @click="$router.push(`/blog/${post.slug}`)">
          <div class="h-48 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center relative overflow-hidden">
            <span class="text-6xl group-hover:scale-110 transition-transform duration-500">{{ post.cover || "📝" }}</span>
          </div>
          <div class="p-6">
            <div class="flex items-center space-x-2 mb-3"><span v-for="tag in post.tags" :key="tag" class="px-2 py-1 text-xs bg-primary-500/20 text-primary-600 dark:text-primary-300 rounded-full">{{ tag }}</span></div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">{{ post.title }}</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm line-clamp-3 mb-4">{{ post.excerpt }}</p>
            <div class="flex items-center justify-between text-sm text-gray-400 dark:text-gray-500"><span>{{ formatDate(post.created_at) }}</span><span>{{ post.read_time }} 分钟阅读</span></div>
          </div>
        </article>
      </div>
      <div v-if="!loading && !error && totalPages > 1" class="mt-12 flex justify-center items-center space-x-2">
        <button @click="goToPage(page - 1)" :disabled="page <= 1" class="px-4 py-2 glass rounded-lg text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors">上一页</button>
        <span class="text-gray-500 dark:text-gray-400 text-sm">{{ page }} / {{ totalPages }}</span>
        <button @click="goToPage(page + 1)" :disabled="page >= totalPages" class="px-4 py-2 glass rounded-lg text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { blogApi } from '@/api'
import { useSEO } from '@/composables/useSEO'

interface BlogPost {
  id: number
  title: string
  slug: string
  excerpt: string
  cover: string | null
  tags: string[]
  read_time: number
  created_at: string
}

const posts = ref<BlogPost[]>([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(1)

function formatDate(dateStr: string) {
  return new Date(dateStr).toISOString().slice(0, 10)
}

async function fetchBlogs() {
  loading.value = true
  error.value = ''
  try {
    const res: any = await blogApi.getList({ page: page.value, page_size: 9 })
    if (res.success && res.data) {
      posts.value = res.data.items
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
  fetchBlogs()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  useSEO({ title: '技术博客', description: '分享技术见解与实践经验' })
  fetchBlogs()
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

