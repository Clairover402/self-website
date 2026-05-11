<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <article class="max-w-4xl mx-auto">
      <header class="mb-12 text-center">
        <div class="flex items-center justify-center space-x-2 mb-4">
          <span
            v-for="tag in post.tags"
            :key="tag"
            class="px-3 py-1 text-sm bg-primary-500/20 text-primary-300 rounded-full"
          >
            {{ tag }}
          </span>
        </div>
        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
          {{ post.title }}
        </h1>
        <div class="flex items-center justify-center space-x-6 text-gray-400 text-sm">
          <span>{{ post.date }}</span>
          <span>{{ post.readTime }} 分钟阅读</span>
        </div>
      </header>

      <div class="glass rounded-2xl p-8 sm:p-12">
        <div class="prose prose-invert prose-lg max-w-none" v-html="renderedContent"></div>
      </div>

      <div class="mt-12 flex justify-between items-center">
        <router-link
          to="/blog"
          class="flex items-center text-gray-400 hover:text-white transition-colors duration-200"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回博客
        </router-link>
        <div class="flex items-center space-x-4">
          <span class="text-gray-500 text-sm">分享到</span>
          <button class="text-gray-400 hover:text-primary-400 transition-colors duration-200">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
            </svg>
          </button>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()

const post = {
  slug: 'vue3-composition-api',
  title: 'Vue 3 Composition API 完全指南',
  tags: ['Vue', '前端'],
  date: '2026-05-01',
  readTime: 8,
  content: `
# Vue 3 Composition API 完全指南

## 引言

Vue 3 引入了全新的 Composition API，这是一种组织组件逻辑的新方式。与传统的 Options API 相比，Composition API 提供了更灵活、更强大的代码组织能力。

## 为什么使用 Composition API？

### 1. 更好的逻辑复用

使用 Composition API，我们可以轻松地将相关逻辑提取到可复用的函数中，称为"组合式函数"（Composables）。

### 2. 更灵活的代码组织

在大型组件中，相关逻辑可能分散在不同的选项中。Composition API 允许我们将相关逻辑放在一起。

### 3. 更好的类型推断

配合 TypeScript，Composition API 提供了更好的类型推断支持。

## 核心概念

### setup() 钩子

\`\`\`javascript
import { ref, computed, onMounted } from 'vue'

export default {
  setup() {
    const count = ref(0)
    const doubled = computed(() => count.value * 2)

    onMounted(() => {
      console.log('Component mounted')
    })

    return { count, doubled }
  }
}
\`\`\`

### 响应式引用

使用 \`ref\` 和 \`reactive\` 创建响应式状态。

### 计算属性

使用 \`computed\` 创建基于响应式数据的计算属性。

## 实际应用

在实际项目中，Composition API 可以帮助我们构建更加模块化和可维护的代码。

## 总结

Composition API 是 Vue 3 最重要的特性之一，掌握它将帮助您构建更好的应用。
  `
}

const renderedContent = computed(() => marked(post.content))
</script>

<style>
.prose h1 { @apply text-3xl font-bold text-white mt-8 mb-4; }
.prose h2 { @apply text-2xl font-semibold text-white mt-6 mb-3; }
.prose h3 { @apply text-xl font-semibold text-white mt-4 mb-2; }
.prose p { @apply text-gray-300 leading-relaxed mb-4; }
.prose ul { @apply list-disc list-inside text-gray-300 mb-4 space-y-1; }
.prose ol { @apply list-decimal list-inside text-gray-300 mb-4 space-y-1; }
.prose code { @apply bg-dark-50 text-primary-300 px-1 py-0.5 rounded text-sm; }
.prose pre { @apply bg-dark-50 rounded-lg p-4 overflow-x-auto mb-4; }
.prose pre code { @apply bg-transparent p-0; }
.prose strong { @apply text-white font-semibold; }
.prose a { @apply text-primary-400 hover:text-primary-300 underline; }
.prose blockquote { @apply border-l-4 border-primary-500 pl-4 italic text-gray-400 my-4; }
</style>
