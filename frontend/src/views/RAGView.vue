<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto text-center">
      <div class="mb-12">
        <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 mb-8 glow-border">
          <div class="w-full h-full rounded-xl bg-gray-100 dark:bg-dark-100 flex items-center justify-center">
            <span class="text-6xl">🤖</span>
          </div>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          AI 知识库
        </h1>
        <p class="text-xl text-gray-500 dark:text-gray-400 mb-8">
          基于 RAG 技术的智能问答系统
        </p>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">即将上线</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-8">
          二期开发中将集成完整的 RAG 能力，包括文档解析、向量检索、大模型问答等功能。
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left mb-8">
          <div
            v-for="feature in features"
            :key="feature"
            class="flex items-center space-x-3 p-4 bg-gray-50/80 dark:bg-dark-50/50 rounded-xl"
          >
            <svg class="w-5 h-5 text-primary-500 dark:text-primary-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="text-gray-600 dark:text-gray-300">{{ feature }}</span>
          </div>
        </div>

        <div class="p-6 bg-primary-500/10 border border-primary-500/30 rounded-xl">
          <p class="text-primary-600 dark:text-primary-300 text-sm">
            <span class="font-semibold">提示：</span>
            当前页面为预留 UI 骨架，RAG 功能将在二期开发中完整实现。
          </p>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/rag/chat"
          class="flex-1 max-w-xs mx-auto flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          体验对话（预留）
        </router-link>
        <router-link
          to="/about"
          class="flex-1 max-w-xs mx-auto flex items-center justify-center px-6 py-3 glass text-gray-900 dark:text-white font-semibold rounded-xl hover:bg-black/5 dark:hover:bg-white/10 transition-all duration-300"
        >
          了解更多
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const features = [
  '多格式文档解析（PDF、Word、Markdown）',
  '语义向量检索',
  'DeepSeek-V4 大模型集成',
  '多知识库分组管理',
  '多轮对话与上下文理解',
  '可视化知识库后台',
  'API 接口开放',
  '私有化部署支持'
]
</script>
