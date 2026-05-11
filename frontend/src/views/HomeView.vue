<template>
  <div class="min-h-screen">
    <section class="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-dark-100 via-dark-50 to-dark-100"></div>
      <div class="absolute inset-0">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      </div>

      <div class="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
        <div class="mb-8 animate-fade-in">
          <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 glow-border">
            <div class="w-full h-full rounded-xl bg-dark-100 flex items-center justify-center">
              <span class="text-5xl">👨‍💻</span>
            </div>
          </div>
        </div>

        <h1 class="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-6 animate-slide-up">
          你好，我是
          <span class="gradient-text">全栈开发者</span>
        </h1>

        <p class="text-xl sm:text-2xl text-gray-300 mb-8 animate-slide-up delay-200">
          专注于现代 Web 技术与人工智能
        </p>

        <p class="text-gray-400 max-w-2xl mx-auto mb-12 animate-slide-up delay-300 leading-relaxed">
          拥有多年全栈开发经验，热衷于构建高性能、可扩展的 Web 应用。
          探索我的作品集和博客，与我一起见证技术的魅力。
        </p>

        <div class="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up delay-400">
          <router-link
            to="/projects"
            class="px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1"
          >
            查看作品集
          </router-link>
          <router-link
            to="/blog"
            class="px-8 py-3 glass text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-300 hover:-translate-y-1"
          >
            阅读博客
          </router-link>
        </div>
      </div>

      <div class="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
        <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>

    <section class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-white text-center mb-16">
          技术栈
        </h2>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-6">
          <div
            v-for="(tech, index) in techStack"
            :key="tech.name"
            class="glass rounded-xl p-6 flex flex-col items-center justify-center hover-lift cursor-pointer group"
            :style="{ animationDelay: `${index * 100}ms` }"
          >
            <div class="text-4xl mb-3 group-hover:scale-110 transition-transform duration-300">
              {{ tech.icon }}
            </div>
            <span class="text-sm text-gray-300">{{ tech.name }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="py-20 px-4 sm:px-6 lg:px-8 bg-dark-50/50">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-white text-center mb-4">
          最新博客
        </h2>
        <p class="text-gray-400 text-center mb-12">分享技术见解与实践经验</p>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <article
            v-for="(post, index) in latestPosts"
            :key="post.slug"
            class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer"
            @click="$router.push(`/blog/${post.slug}`)"
          >
            <div class="h-48 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center">
              <span class="text-6xl opacity-50 group-hover:scale-110 transition-transform duration-300">
                {{ post.cover }}
              </span>
            </div>
            <div class="p-6">
              <div class="flex items-center space-x-2 mb-3">
                <span
                  v-for="tag in post.tags"
                  :key="tag"
                  class="px-2 py-1 text-xs bg-primary-500/20 text-primary-300 rounded-full"
                >
                  {{ tag }}
                </span>
              </div>
              <h3 class="text-lg font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors duration-200">
                {{ post.title }}
              </h3>
              <p class="text-gray-400 text-sm line-clamp-2">
                {{ post.excerpt }}
              </p>
              <div class="mt-4 flex items-center justify-between text-sm text-gray-500">
                <span>{{ post.date }}</span>
                <span>{{ post.readTime }} 分钟阅读</span>
              </div>
            </div>
          </article>
        </div>

        <div class="text-center mt-12">
          <router-link
            to="/blog"
            class="inline-flex items-center text-primary-400 hover:text-primary-300 transition-colors duration-200"
          >
            查看更多
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
    </section>

    <section class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-white text-center mb-4">
          精选项目
        </h2>
        <p class="text-gray-400 text-center mb-12">创新与实践的结晶</p>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div
            v-for="(project, index) in featuredProjects"
            :key="project.id"
            class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer"
            @click="$router.push(`/projects/${project.id}`)"
          >
            <div class="h-56 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center relative overflow-hidden">
              <span class="text-8xl group-hover:scale-110 transition-transform duration-500">
                {{ project.icon }}
              </span>
              <div class="absolute inset-0 bg-gradient-to-t from-dark-100/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end justify-center pb-4">
                <span class="px-4 py-2 bg-primary-500 text-white text-sm rounded-full">查看详情</span>
              </div>
            </div>
            <div class="p-6">
              <h3 class="text-xl font-semibold text-white mb-2 group-hover:text-primary-400 transition-colors duration-200">
                {{ project.name }}
              </h3>
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
          </div>
        </div>

        <div class="text-center mt-12">
          <router-link
            to="/projects"
            class="inline-flex items-center text-primary-400 hover:text-primary-300 transition-colors duration-200"
          >
            查看全部项目
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </div>
    </section>

    <section class="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary-500/10 to-accent-500/10">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-white mb-6">
          准备好开始你的项目了吗？
        </h2>
        <p class="text-gray-400 mb-8">
          无论是合作项目、技术咨询还是只是想聊聊，都可以联系我。
        </p>
        <a
          href="mailto:developer@example.com"
          class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1"
        >
          联系我
          <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </a>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const techStack = [
  { name: 'Vue 3', icon: '⚡' },
  { name: 'TypeScript', icon: '📘' },
  { name: 'Node.js', icon: '🟢' },
  { name: 'Python', icon: '🐍' },
  { name: 'Docker', icon: '🐳' },
  { name: 'PostgreSQL', icon: '🗄️' }
]

const latestPosts = [
  {
    slug: 'vue3-composition-api',
    title: 'Vue 3 Composition API 完全指南',
    excerpt: '深入探索 Vue 3 的 Composition API，学习如何构建更灵活、更可维护的组件。',
    cover: '📚',
    tags: ['Vue', '前端'],
    date: '2026-05-01',
    readTime: 8
  },
  {
    slug: 'fastapi-best-practices',
    title: 'FastAPI 最佳实践',
    excerpt: '掌握 FastAPI 的核心概念，学习如何构建高性能的 Python RESTful API。',
    cover: '🚀',
    tags: ['Python', '后端'],
    date: '2026-04-28',
    readTime: 12
  },
  {
    slug: 'docker-deployment',
    title: 'Docker 容器化部署完全指南',
    excerpt: '从零开始学习 Docker，掌握容器化技术的精髓，实现应用的轻松部署。',
    cover: '🐳',
    tags: ['DevOps', 'Docker'],
    date: '2026-04-25',
    readTime: 10
  }
]

const featuredProjects = [
  {
    id: '1',
    name: 'RAG 智能知识库系统',
    description: '基于向量数据库和 LLM 的智能问答系统，支持多文档解析与多轮对话。',
    icon: '🤖',
    techs: ['Python', 'FastAPI', 'Qdrant', 'Vue 3']
  },
  {
    id: '2',
    name: '实时协作白板',
    description: '支持多人实时协作的在线白板工具，集成绘图、流程图和思维导图功能。',
    icon: '🎨',
    techs: ['React', 'WebSocket', 'Canvas', 'Node.js']
  }
]
</script>

<style scoped>
@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}

.animate-slide-up {
  animation: slide-up 0.6s ease-out forwards;
}

.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-1000 { animation-delay: 1000ms; }

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
