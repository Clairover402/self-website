<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <header class="text-center mb-8">
        <router-link
          to="/rag"
          class="inline-flex items-center text-gray-400 hover:text-white transition-colors duration-200 mb-6"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回 AI 知识库
        </router-link>
        <h1 class="text-3xl font-bold text-white mb-2">智能对话</h1>
        <p class="text-gray-400">基于 RAG 的智能问答系统</p>
      </header>

      <div class="glass rounded-2xl overflow-hidden" style="height: calc(100vh - 280px); min-height: 500px;">
        <div class="flex items-center justify-center h-full">
          <div class="text-center p-8">
            <div class="w-20 h-20 mx-auto rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-6">
              <span class="text-5xl">🔮</span>
            </div>
            <h3 class="text-xl font-semibold text-white mb-4">RAG 功能开发中</h3>
            <p class="text-gray-400 max-w-md mx-auto mb-6">
              智能问答功能正在紧张开发中，预计将在二期与大家见面。届时将支持基于私有知识库的精准问答。
            </p>
            <div class="p-4 bg-dark-50/50 rounded-xl text-left max-w-md mx-auto">
              <p class="text-gray-400 text-sm mb-2 font-medium">二期将支持：</p>
              <ul class="text-gray-300 text-sm space-y-1">
                <li>· PDF/Word 文档上传与解析</li>
                <li>· 向量语义检索</li>
                <li>· DeepSeek-V4 大模型问答</li>
                <li>· 多轮对话上下文记忆</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
</script>
