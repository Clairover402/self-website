<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Hero -->
      <div class="text-center mb-12">
        <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 mb-8 glow-border">
          <div class="w-full h-full rounded-xl bg-gray-100 dark:bg-dark-100 flex items-center justify-center">
            <span class="text-6xl">🤖</span>
          </div>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          AI 知识库
        </h1>
        <p class="text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto">
          基于 RAG 技术的智能问答系统 —— 上传文档，构建你的私有知识库，用自然语言对话获取精准答案
        </p>
      </div>

      <!-- Feature Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="glass rounded-xl p-4 text-center hover:-translate-y-1 transition-transform duration-300"
        >
          <div class="text-3xl mb-2">{{ feature.icon }}</div>
          <h3 class="font-semibold text-gray-900 dark:text-white text-sm">{{ feature.title }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ feature.desc }}</p>
        </div>
      </div>

      <!-- CTA -->
      <div class="text-center">
        <router-link
          to="/rag/chat"
          class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          开始对话
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const features = [
  { icon: "📄", title: "多格式解析", desc: "PDF / Word / MD / HTML" },
  { icon: "🔍", title: "语义检索", desc: "BGE-M3 向量 + BM25" },
  { icon: "🎯", title: "智能重排序", desc: "BGE-reranker-v2-m3" },
  { icon: "💬", title: "流式对话", desc: "DeepSeek-V4 + SSE" },
];
</script>
