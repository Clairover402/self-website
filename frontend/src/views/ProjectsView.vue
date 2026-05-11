<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4">作品集</h1>
        <p class="text-gray-400 text-lg">创新与实践的结晶</p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <article
          v-for="(project, index) in projects"
          :key="project.id"
          class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer"
          :style="{ animationDelay: `${index * 100}ms` }"
          @click="$router.push(`/projects/${project.id}`)"
        >
          <div class="h-64 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center relative overflow-hidden">
            <span class="text-8xl group-hover:scale-110 transition-transform duration-500">
              {{ project.icon }}
            </span>
            <div class="absolute inset-0 bg-gradient-to-t from-dark-100/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-6">
              <span class="px-6 py-2 bg-primary-500 text-white text-sm rounded-full">查看详情</span>
            </div>
          </div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-xl font-semibold text-white group-hover:text-primary-400 transition-colors duration-200">
                {{ project.name }}
              </h3>
              <span class="px-3 py-1 text-xs bg-accent-500/20 text-accent-300 rounded-full">
                {{ project.status }}
              </span>
            </div>
            <p class="text-gray-400 text-sm mb-4">
              {{ project.description }}
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tech in project.techs"
                :key="tech"
                class="px-3 py-1 text-xs bg-dark-50 text-gray-300 rounded-full"
              >
                {{ tech }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const projects = [
  {
    id: '1',
    name: 'RAG 智能知识库系统',
    description: '基于向量数据库和 LLM 的智能问答系统，支持多文档解析与多轮对话。',
    icon: '🤖',
    status: '进行中',
    techs: ['Python', 'FastAPI', 'Qdrant', 'Vue 3', 'LangChain']
  },
  {
    id: '2',
    name: '实时协作白板',
    description: '支持多人实时协作的在线白板工具，集成绘图、流程图和思维导图功能。',
    icon: '🎨',
    status: '已完成',
    techs: ['React', 'WebSocket', 'Canvas', 'Node.js', 'Redis']
  },
  {
    id: '3',
    name: '电商微服务架构',
    description: '基于微服务架构的电商平台，包含用户、商品、订单、支付等核心模块。',
    icon: '🛒',
    status: '已完成',
    techs: ['Go', 'gRPC', 'Docker', 'Kubernetes', 'PostgreSQL']
  },
  {
    id: '4',
    name: 'AI 图像识别平台',
    description: '基于深度学习的图像识别与处理平台，支持多种模型与自定义训练。',
    icon: '🖼️',
    status: '已完成',
    techs: ['Python', 'TensorFlow', 'FastAPI', 'Vue 3', 'MongoDB']
  }
]
</script>
