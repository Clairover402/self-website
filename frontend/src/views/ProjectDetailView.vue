<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <article class="max-w-4xl mx-auto">
      <header class="mb-12">
        <router-link
          to="/projects"
          class="inline-flex items-center text-gray-400 hover:text-white transition-colors duration-200 mb-6"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回作品集
        </router-link>

        <div class="h-64 sm:h-80 bg-gradient-to-br from-primary-500/20 to-accent-500/20 rounded-2xl flex items-center justify-center mb-8">
          <span class="text-9xl">{{ project.icon }}</span>
        </div>

        <div class="flex items-center space-x-3 mb-4">
          <span class="px-3 py-1 text-sm bg-accent-500/20 text-accent-300 rounded-full">
            {{ project.status }}
          </span>
          <span class="text-gray-500">·</span>
          <span class="text-gray-400 text-sm">{{ project.year }}</span>
        </div>

        <h1 class="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
          {{ project.name }}
        </h1>
        <p class="text-xl text-gray-300 leading-relaxed">
          {{ project.description }}
        </p>
      </header>

      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-2xl font-semibold text-white mb-6">项目概述</h2>
        <div class="prose prose-invert max-w-none text-gray-300">
          <p>{{ project.fullDescription }}</p>
        </div>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-2xl font-semibold text-white mb-6">技术栈</h2>
        <div class="flex flex-wrap gap-3">
          <span
            v-for="tech in project.techs"
            :key="tech"
            class="px-4 py-2 bg-dark-50 text-gray-300 rounded-xl"
          >
            {{ tech }}
          </span>
        </div>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-2xl font-semibold text-white mb-6">核心功能</h2>
        <ul class="space-y-4">
          <li
            v-for="feature in project.features"
            :key="feature"
            class="flex items-start space-x-3"
          >
            <svg class="w-6 h-6 text-primary-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span class="text-gray-300">{{ feature }}</span>
          </li>
        </ul>
      </div>

      <div class="flex flex-col sm:flex-row gap-4">
        <a
          href="#"
          class="flex-1 flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300"
        >
          <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          查看源码
        </a>
        <a
          href="#"
          class="flex-1 flex items-center justify-center px-6 py-3 glass text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-300"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
          访问网站
        </a>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const project = {
  id: '1',
  name: 'RAG 智能知识库系统',
  description: '基于向量数据库和 LLM 的智能问答系统，支持多文档解析与多轮对话。',
  icon: '🤖',
  status: '进行中',
  year: '2026',
  fullDescription: '这是一个完整的企业级 RAG（检索增强生成）知识库系统。系统支持多种文档格式上传、智能分块、向量存储和语义检索，可以与大型语言模型结合提供精准的问答服务。多轮对话能力使系统能够理解上下文，提供连贯的交互体验。',
  techs: ['Python', 'FastAPI', 'Qdrant', 'Vue 3', 'LangChain', 'Docker', 'PostgreSQL'],
  features: [
    '支持 PDF、Word、Markdown 等多格式文档解析',
    '基于语义向量的精准检索',
    '支持多知识库分组管理',
    '多轮对话与上下文理解',
    '完整的用户认证与权限管理',
    '可视化知识库管理后台',
    'API 接口支持二次开发'
  ]
}
</script>
