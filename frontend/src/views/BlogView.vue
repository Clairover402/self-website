<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <h1 class="text-4xl sm:text-5xl font-bold text-white mb-4">技术博客</h1>
        <p class="text-gray-400 text-lg">分享技术见解与实践经验</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <article
          v-for="(post, index) in posts"
          :key="post.slug"
          class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer"
          :style="{ animationDelay: `${index * 100}ms` }"
          @click="$router.push(`/blog/${post.slug}`)"
        >
          <div class="h-48 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center relative overflow-hidden">
            <span class="text-6xl group-hover:scale-110 transition-transform duration-500">
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
            <p class="text-gray-400 text-sm line-clamp-3 mb-4">
              {{ post.excerpt }}
            </p>
            <div class="flex items-center justify-between text-sm text-gray-500">
              <span>{{ post.date }}</span>
              <span>{{ post.readTime }} 分钟阅读</span>
            </div>
          </div>
        </article>
      </div>

      <div class="mt-16 flex justify-center">
        <div class="glass rounded-xl px-6 py-4 text-center">
          <p class="text-gray-400 text-sm">更多文章持续更新中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const posts = [
  {
    slug: 'vue3-composition-api',
    title: 'Vue 3 Composition API 完全指南',
    excerpt: '深入探索 Vue 3 的 Composition API，学习如何构建更灵活、更可维护的组件。我们将讨论 setup 钩子、响应式引用、计算属性等核心概念，并提供实际示例帮助您掌握这一强大的工具。',
    cover: '📚',
    tags: ['Vue', '前端'],
    date: '2026-05-01',
    readTime: 8
  },
  {
    slug: 'fastapi-best-practices',
    title: 'FastAPI 最佳实践',
    excerpt: '掌握 FastAPI 的核心概念，学习如何构建高性能的 Python RESTful API。本指南涵盖路径操作、请求验证、依赖注入等关键功能，助您构建生产级别的后端服务。',
    cover: '🚀',
    tags: ['Python', '后端'],
    date: '2026-04-28',
    readTime: 12
  },
  {
    slug: 'docker-deployment',
    title: 'Docker 容器化部署完全指南',
    excerpt: '从零开始学习 Docker，掌握容器化技术的精髓，实现应用的轻松部署。我们将介绍 Docker 核心概念、镜像构建、容器编排以及在实际项目中的应用。',
    cover: '🐳',
    tags: ['DevOps', 'Docker'],
    date: '2026-04-25',
    readTime: 10
  },
  {
    slug: 'typescript-advanced',
    title: 'TypeScript 高级类型技巧',
    excerpt: '深入理解 TypeScript 的高级类型系统，包括泛型、条件类型、映射类型等。通过实际案例展示如何编写更加类型安全的代码，提升开发效率。',
    cover: '📘',
    tags: ['TypeScript', '前端'],
    date: '2026-04-20',
    readTime: 15
  },
  {
    slug: 'postgresql-optimization',
    title: 'PostgreSQL 性能优化实战',
    excerpt: '深入探索 PostgreSQL 的性能优化技巧，包括索引优化、查询分析、连接池配置等。通过实际案例展示如何让数据库查询速度提升数倍。',
    cover: '🗄️',
    tags: ['数据库', 'PostgreSQL'],
    date: '2026-04-15',
    readTime: 11
  },
  {
    slug: 'web-security',
    title: 'Web 安全最佳实践',
    excerpt: '保护您的 Web 应用免受常见安全威胁。本指南涵盖 XSS、CSRF、SQL 注入等安全问题的防护策略，以及 HTTPS、CSP 等安全头部的配置。',
    cover: '🔒',
    tags: ['安全', 'Web'],
    date: '2026-04-10',
    readTime: 9
  }
]
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
