<template>
  <div class="min-h-screen">
    <!-- ===== Hero 鼠标光圈区域 ===== -->
    <section
      class="relative min-h-screen flex items-center justify-center overflow-hidden"
      @mousemove="onMouseMove"
      @mouseleave="onMouseLeave"
      @mouseenter="onMouseEnter"
      @touchmove.prevent="onTouchMove"
      @touchend="onMouseLeave"
    >
      <!-- Layer 1: 中文层（始终可见） -->
      <div class="absolute inset-0 z-10 flex items-center justify-center">
        <div class="absolute inset-0 bg-white dark:bg-dark-100 hero-pattern"></div>
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/20 rounded-full blur-3xl"></div>
        <div class="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
          <div class="mb-8">
            <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 glow-border">
              <div class="w-full h-full rounded-xl bg-dark-100 flex items-center justify-center">
                <span class="text-5xl">👨‍💻</span>
              </div>
            </div>
          </div>
          <h1 class="text-4xl sm:text-5xl md:text-7xl font-extrabold text-gray-900 dark:text-white mb-4 tracking-tight">
            你好，我是 <span class="gradient-text">{{ NAME_ZH }}</span>
          </h1>
          <p class="text-xl sm:text-2xl text-gray-500 dark:text-gray-400 mb-2 font-light">{{ NICKNAME }} · Agent应用全栈开发者</p>
          <p class="text-gray-400 dark:text-gray-500 max-w-xl mx-auto mb-12 leading-relaxed text-sm sm:text-base">
            拥有多年全栈开发经验，热衷于构建高性能、可扩展的 Web 应用。探索我的作品集和博客，与我一起见证技术的魅力。
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <router-link to="/projects" class="px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1">
              查看作品集
            </router-link>
            <router-link to="/blog" class="px-8 py-3 glass text-gray-700 dark:text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-300 hover:-translate-y-1">
              阅读博客
            </router-link>
          </div>
        </div>
      </div>

      <!-- Layer 2: 英文层（clip-path 裁切为光圈） -->
      <div class="absolute inset-0 z-20 flex items-center justify-center" :style="clipStyle">
        <div class="absolute inset-0 bg-dark-100 dark:bg-[#f8fafc] hero-pattern-inverse"></div>
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/10 rounded-full blur-3xl"></div>
        <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl"></div>
        <div class="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto">
          <div class="mb-8">
            <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 glow-border">
              <div class="w-full h-full rounded-xl bg-dark-100 dark:bg-[#f8fafc] flex items-center justify-center">
                <span class="text-5xl">👨‍💻</span>
              </div>
            </div>
          </div>
          <h1 class="text-4xl sm:text-5xl md:text-7xl font-extrabold text-white dark:text-gray-900 mb-4 tracking-tight">
            Hi, I'm <span class="gradient-text">{{ NAME_EN }}</span>
          </h1>
          <p class="text-xl sm:text-2xl text-gray-400 dark:text-gray-600 mb-2 font-light">{{ NICKNAME_EN }} · Agent Application Full-Stack Developer</p>
          <p class="text-gray-400 dark:text-gray-500 max-w-xl mx-auto mb-12 leading-relaxed text-sm sm:text-base">
            Years of full-stack development experience, passionate about building performant, scalable web applications. Explore my portfolio and blog.
          </p>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <router-link to="/projects" class="px-8 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1">
              View Portfolio
            </router-link>
            <router-link to="/blog" class="px-8 py-3 glass text-gray-300 dark:text-gray-700 font-semibold rounded-xl dark:bg-gray-100 dark:border-gray-200 dark:hover:bg-gray-200 hover:bg-white/10 transition-all duration-300 hover:-translate-y-1">
              Read Blog
            </router-link>
          </div>
        </div>
      </div>

      <!-- 光圈辉光环 -->
      <div class="absolute inset-0 z-15 pointer-events-none" :style="glowRingStyle"></div>

      <!-- 向下滚动指示 -->
      <div class="absolute bottom-10 left-1/2 -translate-x-1/2 z-30 animate-bounce">
        <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>

    <!-- 技术栈 -->
    <section ref="techRef" class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white text-center mb-16">技术栈</h2>
        <div v-for="(group, key) in techStack" :key="key" class="mb-10">
          <div class="flex items-center justify-center gap-2 mb-2">
            <span class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{ group.label }}</span>
            <span class="flex-1 h-px bg-white/5"></span>
          </div>
          <div class="flex flex-wrap items-center justify-center gap-4">
            <div v-for="tech in group.items" :key="tech.name" class="glass rounded-xl px-6 py-4 flex items-center gap-3 hover-lift">
              <span class="text-2xl">{{ tech.icon }}</span>
              <span class="text-sm text-gray-600 dark:text-gray-300">{{ tech.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 最新博客 -->
    <section ref="blogRef" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-100/50 dark:bg-dark-50/50">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white text-center mb-4">最新博客</h2>
        <p class="text-gray-500 dark:text-gray-400 text-center mb-12">分享技术见解与实践经验</p>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <article v-for="post in latestPosts" :key="post.slug" class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer" @click="$router.push(`/blog/${post.slug}`)">
            <div class="h-48 bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center">
              <span class="text-6xl opacity-50 group-hover:scale-110 transition-transform duration-300">{{ post.cover }}</span>
            </div>
            <div class="p-6">
              <div class="flex items-center space-x-2 mb-3">
                <span v-for="tag in post.tags" :key="tag" class="px-2 py-1 text-xs bg-primary-500/20 text-primary-600 dark:text-primary-300 rounded-full">{{ tag }}</span>
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">{{ post.title }}</h3>
              <p class="text-gray-500 dark:text-gray-400 text-sm mb-4">{{ post.excerpt }}</p>
              <div class="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>{{ post.date || formatDate(post.created_at) }}</span>
                <span>{{ post.readTime || post.read_time }} 分钟阅读</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- 精选项目 -->
    <section ref="projectsRef" class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white text-center mb-4">精选项目</h2>
        <p class="text-gray-500 dark:text-gray-400 text-center mb-12">创新与实践的结晶</p>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div v-for="project in featuredProjects" :key="project.id" class="glass rounded-2xl overflow-hidden hover-lift group cursor-pointer" @click="$router.push(`/project/${project.id}`)">
            <div class="h-40 bg-gradient-to-br from-primary-500/10 to-accent-500/10 flex items-end justify-center pb-4">
              <span class="px-4 py-2 bg-primary-500 text-white text-sm rounded-full">查看详情</span>
            </div>
            <div class="p-6">
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors duration-200">{{ project.name }}</h3>
              <p v-if="project.status" class="text-xs text-gray-400 dark:text-gray-500 mt-1">{{ project.status }}</p>
              <p class="text-gray-500 dark:text-gray-400 text-sm mb-4">{{ project.description }}</p>
              <div class="flex flex-wrap gap-2">
                <span v-for="tech in project.techs" :key="tech" class="px-3 py-1 text-xs bg-gray-100 dark:bg-dark-50 text-gray-600 dark:text-gray-300 rounded-full">{{ tech }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="text-center mt-12">
          <router-link to="/projects" class="inline-flex items-center text-primary-500 dark:text-primary-400 hover:text-primary-600 dark:hover:text-primary-300 transition-colors duration-200">
            查看全部项目
            <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 技术能力 -->
    <section ref="skillsRef" class="py-20 px-4 sm:px-6 lg:px-8 bg-gray-100/50 dark:bg-dark-50/50">
      <div class="max-w-4xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white text-center mb-4">技术能力</h2>
        <p class="text-gray-500 dark:text-gray-400 text-center mb-12">全栈技能分布一览</p>
        <SkillRadar v-if="showRadar" :skills="radarSkills" />
        <div v-else class="h-80 flex items-center justify-center text-gray-400">加载中...</div>
      </div>
    </section>

    <!-- 联系我 -->
    <section ref="contactRef" class="py-20 px-4 sm:px-6 lg:px-8">
      <div class="max-w-2xl mx-auto">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white text-center mb-4">联系我</h2>
        <p class="text-gray-500 dark:text-gray-400 text-center mb-12">有任何问题或合作意向，欢迎留言</p>
        <form @submit.prevent="submitContact" class="space-y-4">
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">姓名</label>
            <input v-model="contactForm.name" type="text" required class="w-full px-4 py-3 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-colors" placeholder="你的名字" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">邮箱</label>
            <input v-model="contactForm.email" type="email" required class="w-full px-4 py-3 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-colors" placeholder="your@email.com" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-300 mb-2">留言</label>
            <textarea v-model="contactForm.message" rows="4" required class="w-full px-4 py-3 bg-white dark:bg-white/5 border border-gray-200 dark:border-white/10 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-colors resize-none" placeholder="想说点什么..."></textarea>
          </div>
          <button type="submit" :disabled="contactSending" class="w-full py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 disabled:opacity-50">
            {{ contactSending ? '发送中...' : '发送留言' }}
          </button>
          <p v-if="contactSuccess" class="text-emerald-500 text-center text-sm">{{ contactSuccess }}</p>
          <p v-if="contactError" class="text-red-400 text-center text-sm">{{ contactError }}</p>
        </form>
      </div>
    </section>

    <!-- CTA -->
    <section ref="ctaRef" class="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary-500/10 to-accent-500/10">
      <div class="max-w-4xl mx-auto text-center">
        <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 dark:text-white mb-6">准备好开始你的项目了吗？</h2>
        <p class="text-gray-500 dark:text-gray-400 mb-8">无论是合作项目、技术咨询还是只是想聊聊，都可以联系我。</p>
        <a href="mailto:developer@example.com" class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-primary-500 to-accent-500 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1">
          联系我
          <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
        </a>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, defineAsyncComponent } from 'vue'
import { blogApi, projectApi } from '@/api'
import { useSEO } from '@/composables/useSEO'
import { useScrollReveal } from '@/composables/useScrollReveal'
import axios from 'axios'

const SkillRadar = defineAsyncComponent(() => import('@/components/SkillRadar.vue'))

// ===== Scroll Reveal Refs =====
const techRef = ref<HTMLElement | null>(null)
const blogRef = ref<HTMLElement | null>(null)
const projectsRef = ref<HTMLElement | null>(null)
const skillsRef = ref<HTMLElement | null>(null)
const contactRef = ref<HTMLElement | null>(null)
const ctaRef = ref<HTMLElement | null>(null)

// ===== 个人信息 =====
const NAME_ZH = '张昊'
const NAME_EN = 'Zhang Hao'
const NICKNAME = '花月'
const NICKNAME_EN = 'Huayue'

// ===== 技术栈 =====
const techStack = {
  python: { label: 'Python', items: [
    { name: 'Python', icon: '🐍' },
    { name: 'FastAPI', icon: '⚡' },
    { name: 'RAG', icon: '🧠' },
  ]},
  java: { label: 'Java', items: [
    { name: 'Java', icon: '☕' },
    { name: 'Spring', icon: '🍃' },
    { name: 'SpringBoot', icon: '🖥️' },
  ]},
  other: { label: 'Infrastructure', items: [
    { name: 'Redis', icon: '🔴' },
    { name: 'MySQL', icon: '🐬' },
    { name: 'Docker', icon: '🐳' },
  ]},
}

// ===== 博客 / 项目数据 =====
const latestPosts = ref([
  { slug: 'vue3-composition-api', title: 'Vue 3 Composition API 完全指南', excerpt: '深入探索 Vue 3 的 Composition API。', cover: '📗', tags: ['Vue','前端'], date: '2026-05-01', readTime: 8 },
  { slug: 'fastapi-best-practices', title: 'FastAPI 最佳实践', excerpt: '掌握 FastAPI 的核心概念。', cover: '🚀', tags: ['Python','后端'], date: '2026-04-28', readTime: 12 },
  { slug: 'docker-deployment', title: 'Docker 容器化部署完全指南', excerpt: '从零开始学习 Docker。', cover: '🐳', tags: ['DevOps','Docker'], date: '2026-04-25', readTime: 10 },
])

const featuredProjects = ref([
  { id: '1', name: 'RAG 智能知识库系统', description: '基于向量数据库和 LLM 的智能问答系统。', icon: '🤖', status: '进行中', techs: ['Python','FastAPI','Qdrant','Vue 3'] },
  { id: '2', name: '实时协作白板', description: '支持多人实时协作的在线白板工具。', icon: '🎨', status: '已完成', techs: ['React','WebSocket','Canvas','Node.js'] },
])

function formatDate(d: string) { return d ? new Date(d).toISOString().slice(0, 10) : '' }

async function fetchHomeData() {
  try {
    const [b, p] = await Promise.all([
      blogApi.getList({ page_size: 3 }),
      projectApi.getList({ page_size: 2 }),
    ])
    const bData: any = b; if (bData.success && bData.data?.items?.length) {
      latestPosts.value = bData.data.items.map((i: any) => ({ ...i, date: formatDate(i.created_at), readTime: i.read_time }))
    }
    const pData: any = p; if (pData.success && pData.data?.items?.length) {
      featuredProjects.value = pData.data.items
    }
  } catch { /* keep fallback */ }
}

// ===== 技能雷达 =====
const showRadar = ref(false)
const radarSkills = [
  { name: 'Vue / 前端', value: 90 },
  { name: 'TypeScript', value: 85 },
  { name: 'Python / 后端', value: 82 },
  { name: '数据库', value: 78 },
  { name: 'DevOps / Docker', value: 72 },
  { name: 'AI / ML', value: 68 },
]

// ===== 鼠标光圈 =====
const spotlightX = ref(0)
const spotlightY = ref(0)
const spotlightRadius = ref(0)
const targetX = ref(0)
const targetY = ref(0)
const targetRadius = ref(0)
let rafId = 0

const clipStyle = computed(() => ({
  clipPath: `circle(${spotlightRadius.value}px at ${spotlightX.value}px ${spotlightY.value}px)`,
}))

const glowRingStyle = computed(() => ({
  background: `radial-gradient(circle ${spotlightRadius.value}px at ${spotlightX.value}px ${spotlightY.value}px, rgba(14, 165, 233, 0.15) 0%, rgba(14, 165, 233, 0.05) 70%, transparent 100%)`,
  opacity: spotlightRadius.value > 10 ? 1 : 0,
  transition: 'opacity 0.2s ease',
}))

function getRadius() {
  return Math.max(120, Math.min(window.innerWidth, window.innerHeight) * 0.3)
}

function lerp(current: number, target: number, factor: number) {
  return current + (target - current) * factor
}

function animate() {
  spotlightX.value = lerp(spotlightX.value, targetX.value, 0.08)
  spotlightY.value = lerp(spotlightY.value, targetY.value, 0.08)
  spotlightRadius.value = lerp(spotlightRadius.value, targetRadius.value, 0.12)
  if (spotlightRadius.value < 1 && targetRadius.value === 0) spotlightRadius.value = 0
  rafId = requestAnimationFrame(animate)
}

function onMouseMove(e: MouseEvent) {
  targetX.value = e.clientX
  targetY.value = e.clientY
  targetRadius.value = getRadius()
}
function onMouseEnter() { targetRadius.value = getRadius() }
function onMouseLeave() { targetRadius.value = 0 }
function onTouchMove(e: TouchEvent) {
  const touch = e.touches[0]
  targetX.value = touch.clientX
  targetY.value = touch.clientY
  targetRadius.value = getRadius()
}

// ===== 联系表单 =====
const contactForm = ref({ name: '', email: '', message: '' })
const contactSending = ref(false)
const contactSuccess = ref('')
const contactError = ref('')

async function submitContact() {
  contactSending.value = true
  contactSuccess.value = ''
  contactError.value = ''
  try {
    await axios.post('/api/contact', contactForm.value)
    contactSuccess.value = '留言已发送，感谢联系！'
    contactForm.value = { name: '', email: '', message: '' }
  } catch {
    contactError.value = '发送失败，请稍后重试'
  } finally { contactSending.value = false }
}

useScrollReveal([
  { ref: techRef, childSelector: '.glass.rounded-xl', stagger: 0.1 },
  { ref: blogRef, childSelector: 'article', stagger: 0.15 },
  { ref: projectsRef, childSelector: '.glass.rounded-2xl', stagger: 0.15 },
  { ref: skillsRef, onEnter: () => { if (!showRadar.value) showRadar.value = true } },
  { ref: contactRef, childSelector: 'input, textarea, button', stagger: 0.1 },
  { ref: ctaRef },
])

onMounted(() => {
  fetchHomeData()
  useSEO({ title: NAME_ZH + ' ' + NICKNAME + ' - Agent Application Full-Stack Developer', description: 'Portfolio, Tech Blog & AI Knowledge Base', keywords: 'fullstack,developer,Vue,Python,AI,blog' })
  spotlightX.value = window.innerWidth / 2
  spotlightY.value = window.innerHeight / 2
  targetX.value = spotlightX.value
  targetY.value = spotlightY.value
  animate()
})

onUnmounted(() => { cancelAnimationFrame(rafId) })
</script>
  { ref: skillsRef, onEnter: () => { if (!showRadar.value) showRadar.value = true } },
