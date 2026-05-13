<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-16">
        <div class="w-40 h-40 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 mb-8 glow-border">
          <div class="w-full h-full rounded-xl bg-white dark:bg-dark-100 flex items-center justify-center">
            <span class="text-7xl">👨‍💻</span>
          </div>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">关于我</h1>
        <p class="text-xl text-gray-600 dark:text-gray-400">全栈开发者 · 技术博主 · 开源贡献者</p>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">个人简介</h2>
        <div class="prose dark:prose-invert max-w-none text-gray-600 dark:text-gray-300 space-y-4">
          <p>你好！我是一名拥有多年全栈开发经验的开发者，专注于现代 Web 技术和人工智能领域。我热衷于构建高性能、可扩展的应用，并乐于分享技术知识和经验。</p>
          <p>在过去的几年里，我参与了多个大型项目的开发，涵盖电商、社交、AI 等多个领域。我熟悉从前端到后端、从开发到部署的完整技术栈。</p>
          <p>除了工作，我也积极维护开源项目，撰写技术博客，希望能为技术社区贡献自己的一份力量。</p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="glass rounded-2xl p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <span class="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center mr-3"><span>💼</span></span>
            工作经历
          </h3>
          <div class="space-y-4">
            <div class="border-l-2 border-primary-500 pl-4">
              <h4 class="text-gray-900 dark:text-white font-medium">高级全栈工程师</h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm">某科技公司 · 2022 - 至今</p>
            </div>
            <div class="border-l-2 border-primary-500 pl-4">
              <h4 class="text-gray-900 dark:text-white font-medium">全栈开发工程师</h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm">某互联网公司 · 2019 - 2022</p>
            </div>
          </div>
        </div>

        <div class="glass rounded-2xl p-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <span class="w-8 h-8 rounded-lg bg-accent-500/20 flex items-center justify-center mr-3"><span>🎓</span></span>
            教育背景
          </h3>
          <div class="space-y-4">
            <div class="border-l-2 border-accent-500 pl-4">
              <h4 class="text-gray-900 dark:text-white font-medium">计算机科学与技术</h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm">某重点大学 · 2015 - 2019</p>
            </div>
          </div>
        </div>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">技术栈</h3>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div v-for="skill in skills" :key="skill.category" class="text-center p-4 bg-gray-100 dark:bg-dark-50/50 rounded-xl">
            <div class="text-2xl mb-2">{{ skill.icon }}</div>
            <h4 class="text-gray-900 dark:text-white font-medium mb-2">{{ skill.category }}</h4>
            <p class="text-gray-600 dark:text-gray-400 text-sm">{{ skill.items.join(' · ') }}</p>
          </div>
        </div>
      </div>

      <div class="glass rounded-2xl p-8 mb-8">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-6 flex items-center">
          <span class="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center mr-3"><span>🏆</span></span>
          获得奖项
        </h3>
        <div v-if="awards.length === 0" class="text-gray-600 dark:text-gray-400 text-center py-4">暂无奖项数据</div>
        <div v-else class="space-y-3">
          <div v-for="award in awards" :key="award.id"
            class="flex items-center justify-between p-4 bg-gray-100 dark:bg-dark-50/50 rounded-xl hover:bg-gray-200 dark:hover:bg-white/5 transition-colors duration-200">
            <div class="flex-1 min-w-0">
              <h4 class="text-gray-900 dark:text-white font-medium truncate">{{ award.title }}</h4>
              <p class="text-gray-600 dark:text-gray-400 text-sm mt-0.5">{{ award.organization }} · {{ award.award_date }}</p>
            </div>
            <span :class="['ml-4 px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap', levelBadge(award.level)]">
              {{ award.level }}
            </span>
          </div>
        </div>
      </div>

      <div class="glass rounded-2xl p-8">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">联系方式</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <a v-for="contact in contacts" :key="contact.label" :href="contact.href"
            class="flex items-center p-4 bg-gray-100 dark:bg-dark-50/50 rounded-xl hover:bg-gray-200 dark:hover:bg-white/5 transition-colors duration-200">
            <span class="text-2xl mr-4">{{ contact.icon }}</span>
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm">{{ contact.label }}</p>
              <p class="text-gray-900 dark:text-white">{{ contact.value }}</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { awardApi } from '@/api'

const skills = [
  { category: '前端', icon: '🎨', items: ['Vue 3', 'React', 'TypeScript', 'Tailwind CSS'] },
  { category: '后端', icon: '⚙️', items: ['Python', 'Go', 'Node.js', 'FastAPI'] },
  { category: '数据库', icon: '🗄️', items: ['PostgreSQL', 'MongoDB', 'Redis', 'Qdrant'] },
  { category: 'DevOps', icon: '🚀', items: ['Docker', 'Kubernetes', 'CI/CD', 'Linux'] },
  { category: 'AI/ML', icon: '🤖', items: ['LangChain', 'TensorFlow', 'PyTorch', 'RAG'] },
  { category: '工具', icon: '🔧', items: ['Git', 'Vim', 'VS Code', 'Figma'] }
]

const contacts = [
  { label: '邮箱', value: 'developer@example.com', href: 'mailto:developer@example.com', icon: '📧' },
  { label: 'GitHub', value: 'github.com/developer', href: 'https://github.com', icon: '🐙' },
  { label: 'Twitter', value: '@developer', href: 'https://twitter.com', icon: '🐦' },
  { label: '博客', value: 'blog.example.com', href: 'https://blog.example.com', icon: '📝' }
]

interface Award {
  id: number
  title: string
  organization: string
  award_date: string
  level: string
}

const awards = ref<Award[]>([])

onMounted(async () => {
  try {
    const res: any = await awardApi.getList({ page_size: 100 })
    if (res?.success && res.data?.items) {
      awards.value = res.data.items
    }
  } catch {
    // silently fail, show empty state
  }
})

function levelBadge(level: string): string {
  const map: Record<string, string> = {
    '国家级': 'bg-amber-500/20 text-amber-600 dark:text-amber-400 border border-amber-500/30',
    '省级': 'bg-blue-500/20 text-blue-600 dark:text-blue-400 border border-blue-500/30',
    '市级': 'bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30',
    '校级': 'bg-purple-500/20 text-purple-600 dark:text-purple-400 border border-purple-500/30',
    '一等奖': 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400 border border-yellow-500/30',
    '二等奖': 'bg-gray-500/20 text-gray-600 dark:text-gray-300 border border-gray-500/30',
    '三等奖': 'bg-orange-500/20 text-orange-600 dark:text-orange-400 border border-orange-500/30',
    '优秀奖': 'bg-teal-500/20 text-teal-600 dark:text-teal-400 border border-teal-500/30',
    '其他': 'bg-slate-500/20 text-slate-600 dark:text-slate-400 border border-slate-500/30',
  }
  return map[level] || 'bg-slate-500/20 text-slate-600 dark:text-slate-400 border border-slate-500/30'
}
</script>