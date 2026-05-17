<template>
  <div class="min-h-screen py-12 px-4">
    <div class="max-w-5xl mx-auto">
      <div v-if="!token" class="max-w-sm mx-auto mt-20">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-8 text-center">Admin Panel</h1>
        <form @submit.prevent="doLogin" class="space-y-4">
          <input v-model="password" type="password" placeholder="Password" class="w-full px-4 py-3 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500" />
          <button type="submit" :disabled="loginLoading" class="w-full py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors disabled:opacity-50">{{ loginLoading ? 'Logging in...' : 'Login' }}</button>
          <p v-if="loginError" class="text-red-400 text-sm text-center">{{ loginError }}</p>
        </form>
      </div>

      <div v-else>
        <div class="flex items-center justify-between mb-8">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Admin Panel</h1>
          <button @click="logout" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white transition-colors">Logout</button>
        </div>

        <div class="flex flex-wrap gap-2 mb-8">
          <button v-for="tab in tabs" :key="tab.key" @click="switchTab(tab.key)" :class="activeTab === tab.key ? clsActive : clsInactive">{{ tab.label }}</button>
        </div>

        <!-- Blogs -->
        <div v-if="activeTab === 'blogs'" class="space-y-4">
          <button @click="openBlogForm()" class="px-4 py-2 bg-primary-500 text-white text-sm rounded-lg hover:bg-primary-600 transition-colors mb-4">New Blog</button>
          <div v-for="item in blogList" :key="item.id" class="glass rounded-xl p-4 flex items-center justify-between">
            <div><p class="text-gray-900 dark:text-white font-medium">{{ item.title }}</p><p class="text-gray-500 dark:text-gray-400 text-sm">{{ item.slug }} &middot; {{ formatDate(item.created_at) }}</p></div>
            <div class="flex space-x-2">
              <button @click="openBlogForm(item)" class="px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300">Edit</button>
              <button @click="deleteBlog(item.slug)" class="px-3 py-1 text-sm text-red-400 hover:text-red-300">Delete</button>
            </div>
          </div>
        </div>

        <!-- Projects -->
        <div v-if="activeTab === 'projects'" class="space-y-4">
          <button @click="openProjectForm(null)" class="px-4 py-2 bg-primary-500 text-white text-sm rounded-lg hover:bg-primary-600 transition-colors mb-4">New Project</button>
          <div v-for="item in projectList" :key="item.id" class="glass rounded-xl p-4 flex items-center justify-between">
            <div><p class="text-gray-900 dark:text-white font-medium">{{ item.name }}</p><p class="text-gray-500 dark:text-gray-400 text-sm">{{ item.status }}</p></div>
            <div class="flex space-x-2">
              <button @click="openProjectForm(item)" class="px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300">Edit</button>
              <button @click="deleteProject(item.id)" class="px-3 py-1 text-sm text-red-400 hover:text-red-300">Delete</button>
            </div>
          </div>
        </div>

        <!-- Awards -->
        <div v-if="activeTab === 'awards'" class="space-y-4">
          <button @click="openAwardForm(null)" class="px-4 py-2 bg-primary-500 text-white text-sm rounded-lg hover:bg-primary-600 transition-colors mb-4">New Award</button>
          <div v-for="item in awardList" :key="item.id" class="glass rounded-xl p-4 flex items-center justify-between">
            <div><p class="text-gray-900 dark:text-white font-medium">{{ item.title }}</p><p class="text-gray-500 dark:text-gray-400 text-sm">{{ item.organization }} &middot; {{ item.level }}</p></div>
            <div class="flex space-x-2">
              <button @click="openAwardForm(item)" class="px-3 py-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300">Edit</button>
              <button @click="deleteAward(item.id)" class="px-3 py-1 text-sm text-red-400 hover:text-red-300">Delete</button>
            </div>
          </div>
        </div>

        <!-- Contacts -->
        <div v-if="activeTab === 'contacts'" class="space-y-4">
          <div v-for="item in contactList" :key="item.id" class="glass rounded-xl p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-gray-900 dark:text-white font-medium">{{ item.name }}</span>
              <span class="text-gray-500 dark:text-gray-400 text-sm">{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="text-gray-500 dark:text-gray-400 text-sm mb-1">{{ item.email }}</p>
            <p class="text-gray-700 dark:text-gray-300 text-sm">{{ item.message }}</p>
          </div>
        </div>

        <!-- RAG -->
        <div v-if="activeTab === 'rag'" class="space-y-6">
          <!-- Create KB -->
          <div class="glass rounded-xl p-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-3">新建知识库</h3>
            <div class="flex flex-wrap gap-3">
              <input v-model="newKbName" type="text" placeholder="知识库名称" class="flex-1 min-w-[180px] px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-primary-500" />
              <input v-model="newKbDesc" type="text" placeholder="描述（可选）" class="flex-1 min-w-[180px] px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-primary-500" />
              <textarea v-model="newKbContent" placeholder="知识库内容（可选，将自动生成为文档）" rows="3" class="w-full px-3 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-primary-500 font-mono"></textarea>
              <label class="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                <input v-model="newKbDefault" type="checkbox" class="rounded" /> 默认
              <select v-model="newKbVisibility" class="px-2 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg text-sm">
                <option value="private">私有</option>
                <option value="public">公开访问</option>
              </select>
              </label>
              <button @click="createKb" :disabled="!newKbName.trim()" class="px-4 py-2 bg-primary-500 text-white text-sm rounded-lg hover:bg-primary-600 disabled:opacity-50 transition-colors">创建</button>
            </div>
          </div>

          <!-- KB List -->
          <div v-if="kbList.length === 0 && !ragLoading" class="text-center py-8 text-gray-400">暂无知识库</div>
          <div v-for="kb in kbList" :key="kb.id" class="glass rounded-xl overflow-hidden">
            <div class="p-4 flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ kb.name }}</h3>
                  <span v-if="kb.is_default" class="px-2 py-0.5 text-xs rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300">默认</span>
                </div>
                <p v-if="kb.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ kb.description }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ kb._documents?.length || 0 }} 个文档</p>
              </div>
              <div class="flex items-center gap-2">
                <label :for="'rag-upload-' + kb.id" class="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 cursor-pointer transition-colors">上传文档</label>
                <input :id="'rag-upload-' + kb.id" type="file" accept=".pdf,.docx,.md,.html,.txt" class="hidden" @change="(e) => handleUpload(kb.id, e)" />
                <button @click="toggleKbExpand(kb.id)" class="px-3 py-1.5 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white transition-colors">{{ expandedKb === kb.id ? '收起' : '展开' }}</button>
                <button @click="deleteKb(kb.id)" class="px-3 py-1.5 text-xs text-red-400 hover:text-red-300 transition-colors">删除</button>
              </div>
            </div>

            <!-- Documents -->
            <div v-if="expandedKb === kb.id" class="border-t border-gray-200 dark:border-gray-700 px-4 py-3 bg-gray-50 dark:bg-gray-800/50">
              <div v-if="!kb._documents || kb._documents.length === 0" class="text-sm text-gray-400 py-2">暂无文档</div>
              <div v-for="doc in kb._documents" :key="doc.id" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
                <div class="flex items-center gap-2">
                  <span :class="['inline-block w-2 h-2 rounded-full', doc.status === 'completed' ? 'bg-green-400' : doc.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400']"></span>
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ doc.filename }}</span>
                  <span class="text-xs text-gray-400">({{ doc.chunk_count }} chunks)</span>
                </div>
                <button @click="deleteDoc(doc.id, kb.id)" class="text-xs text-red-400 hover:text-red-300 transition-colors">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Blog Form Modal -->
        <div v-if="showBlogForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showBlogForm = false">
          <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingBlog ? 'Edit' : 'New' }} Blog</h2>
            <div class="space-y-3">
              <input v-model="blogForm.title" placeholder="Title" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="blogForm.slug" placeholder="Slug" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="blogForm.excerpt" placeholder="Excerpt" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="blogForm.cover" placeholder="Cover URL" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="blogForm.tagsStr" placeholder="Tags (comma separated)" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <div class="flex items-center space-x-3">
              <select v-model="blogForm.content_type" class="px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none">
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
              <label v-if="blogForm.content_type === 'html'" class="px-3 py-2 bg-gray-100 dark:bg-gray-600 text-sm rounded-lg cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-500 transition-colors">
                <input type="file" accept=".html,.htm" class="hidden" @change="loadHtmlFile" />
                Upload HTML
              </label>
            </div>
            <textarea v-model="blogForm.content" :placeholder="blogForm.content_type === 'html' ? 'Content (HTML)' : 'Content (Markdown)'" rows="12" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none font-mono"></textarea>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showBlogForm = false" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white">Cancel</button>
              <button @click="saveBlog" :disabled="saving" class="px-4 py-2 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
            </div>
          </div>
        </div>

        <!-- Award Form Modal (placeholder - kept minimal) -->
        <div v-if="showAwardForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showAwardForm = false">
          <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-xl w-full mx-4">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingAward ? 'Edit' : 'New' }} Award</h2>
            <div class="space-y-3">
              <input v-model="awardForm.title" placeholder="Title" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="awardForm.organization" placeholder="Organization" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="awardForm.award_date" type="date" placeholder="获奖日期" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <select v-model="awardForm.level" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none">
                <option value="">选择级别</option>
                <option value="国家级">国家级</option><option value="省级">省级</option><option value="市级">市级</option><option value="校级">校级</option>
                <option value="一等奖">一等奖</option><option value="二等奖">二等奖</option><option value="三等奖">三等奖</option>
                <option value="优秀奖">优秀奖</option><option value="其他">其他</option>
              </select>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showAwardForm = false" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white">Cancel</button>
              <button @click="saveAward" :disabled="saving" class="px-4 py-2 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
            </div>
          </div>
        </div>
        <!-- Project Form Modal -->
        <div v-if="showProjectForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showProjectForm = false">
          <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingProject ? 'Edit' : 'New' }} Project</h2>
            <div class="space-y-3">
              <div class="grid grid-cols-2 gap-3">
                <input v-model="projectForm.name" placeholder="Name *" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
                <select v-model="projectForm.status" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none">
                  <option value="">Status</option>
                  <option value="planning">Planning</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="maintenance">Maintenance</option>
                </select>
              </div>
              <input v-model="projectForm.description" placeholder="Short description" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="projectForm.icon" placeholder="Icon (emoji)" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="projectForm.year" placeholder="Year" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="projectForm.techsStr" placeholder="Techs (comma separated)" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="projectForm.demo_url" placeholder="Demo URL" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <input v-model="projectForm.repo_url" placeholder="Repo URL" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
              <textarea v-model="projectForm.full_description" placeholder="Full description (Markdown)" rows="6" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none font-mono"></textarea>
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showProjectForm = false" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white">Cancel</button>
              <button @click="saveProject" :disabled="saving" class="px-4 py-2 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { blogApi, projectApi, awardApi, adminApi, adminRagApi } from '@/api'

const token = ref(localStorage.getItem('admin_token') || '')
const password = ref('')
const loginLoading = ref(false)
const loginError = ref('')
const activeTab = ref('blogs')
const saving = ref(false)
const ragLoading = ref(false)

const clsActive = 'px-4 py-2 rounded-lg text-sm bg-primary-500 text-white transition-colors'
const clsInactive = 'px-4 py-2 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white glass transition-colors'

const tabs = [
  { key: 'blogs', label: 'Blogs' },
  { key: 'projects', label: 'Projects' },
  { key: 'awards', label: 'Awards' },
  { key: 'contacts', label: 'Contacts' },
  { key: 'rag', label: 'RAG' },
]

const blogList = ref<any[]>([])
const projectList = ref<any[]>([])
const awardList = ref<any[]>([])
const contactList = ref<any[]>([])
const kbList = ref<any[]>([])

// RAG state
const newKbName = ref('')
const newKbDesc = ref('')
const newKbDefault = ref(false)
const newKbVisibility = ref("private")
const newKbContent = ref('')
const expandedKb = ref<string | null>(null)

function formatDate(d: string) { return d ? new Date(d).toISOString().slice(0, 10) : '' }
function logout() { token.value = ''; localStorage.removeItem('admin_token') }

function switchTab(key: string) {
  activeTab.value = key
  if (key === 'rag') loadRag()
}

async function doLogin() {
  loginLoading.value = true
  loginError.value = ''
  try {
    const res: any = await adminApi.login(password.value)
    if (res?.success && res?.data?.token) {
      token.value = res.data.token
      localStorage.setItem('admin_token', token.value)
      loadAll()
    } else { loginError.value = 'Invalid password' }
  } catch { loginError.value = 'Login failed' }
  finally { loginLoading.value = false }
}

async function loadAll() {
  try {
    const [b, p, a, c] = await Promise.all([
      blogApi.getList({ page_size: 100 }),
      projectApi.getList({ page_size: 100 }),
      awardApi.getList({ page_size: 100 }),
      adminApi.listContacts(),
    ])
    blogList.value = (b as any)?.data?.items || []
    projectList.value = (p as any)?.data?.items || []
    awardList.value = (a as any)?.data?.items || []
    contactList.value = (c as any)?.data || []
  } catch (e) { console.error('Failed to load admin data', e) }
}

// ===== RAG =====

async function loadRag() {
  ragLoading.value = true
  try {
    const res: any = await adminRagApi.getKnowledgeBases()
    kbList.value = res?.data || []
    // Load documents for each KB
    for (const kb of kbList.value) {
      try {
        const docRes: any = await adminRagApi.getDocuments(kb.id)
        kb._documents = docRes?.data || []
      } catch { kb._documents = [] }
    }
  } catch (e) { console.error('Failed to load RAG data', e) }
  finally { ragLoading.value = false }
}

async function createKb() {
  if (!newKbName.value.trim()) return
  try {
    const res: any = await adminRagApi.createKnowledgeBase({
      name: newKbName.value.trim(),
      description: newKbDesc.value.trim() || undefined,
      is_default: newKbDefault.value,
    })
    const kbId = res?.data?.id
    // If content was provided, upload it as a text document
    if (kbId && newKbContent.value.trim()) {
      const blob = new Blob([newKbContent.value], { type: 'text/plain' })
      const file = new File([blob], newKbName.value.trim() + '.txt', { type: 'text/plain' })
      await adminRagApi.uploadDocument(kbId, file)
    }
    newKbName.value = ''
    newKbDesc.value = ''
    newKbDefault.value = false
    newKbContent.value = ''
    await loadRag()
  } catch (e) { console.error('Failed to create KB', e); alert('创建知识库失败，请检查控制台') }
}

async function deleteKb(kbId: string) {
  if (!confirm('确定删除该知识库及其所有文档？')) return
  try {
    await adminRagApi.deleteKnowledgeBase(kbId)
    await loadRag()
  } catch (e) { console.error('Failed to delete KB', e) }
}

function toggleKbExpand(kbId: string) {
  expandedKb.value = expandedKb.value === kbId ? null : kbId
}

async function handleUpload(kbId: string, event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    await adminRagApi.uploadDocument(kbId, file)
    await loadRag()
  } catch (e) { console.error('Upload failed', e); alert('上传失败，请重试') }
  finally { input.value = '' }
}

async function deleteDoc(docId: string, _kbId: string) {
  if (!confirm('确定删除该文档？')) return
  try {
    await adminRagApi.deleteDocument(docId)
    await loadRag()
  } catch (e) { console.error('Failed to delete doc', e) }
}

// Blog
const showBlogForm = ref(false)
const editingBlog = ref<any>(null)
const blogForm = ref({ title: '', slug: '', excerpt: '', content: '', cover: '', tagsStr: '', content_type: 'markdown' })

function openBlogForm(item?: any) {
  editingBlog.value = item || null
  blogForm.value = item
    ? { title: item.title, slug: item.slug, excerpt: item.excerpt, content: item.content, cover: item.cover || '', tagsStr: (item.tags || []).join(','), content_type: item.content_type || 'markdown' }
    : { title: '', slug: '', excerpt: '', content: '', cover: '', tagsStr: '', content_type: 'markdown' }
  showBlogForm.value = true
}

async function saveBlog() {
  saving.value = true
  try {
    const payload = { ...blogForm.value, tags: blogForm.value.tagsStr.split(',').map((s: string) => s.trim()).filter(Boolean), read_time: 5 }
    if (editingBlog.value) {
      await adminApi.updateBlog(editingBlog.value.slug, payload)
    } else {
      await adminApi.createBlog(payload)
    }
    showBlogForm.value = false
    loadAll()
  } catch (e) { console.error('Failed to save blog', e); alert('保存失败，请重试') }
  finally { saving.value = false }
}

async function deleteBlog(slug: string) {
  if (!confirm('Delete?')) return
  try { await adminApi.deleteBlog(slug); loadAll() } catch (e) { console.error('Failed to delete blog', e); alert('删除失败，请重试') }
}

function loadHtmlFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => { blogForm.value.content = reader.result as string }
  reader.readAsText(file)
}

// Project
const showProjectForm = ref(false)
const editingProject = ref<any>(null)
const projectForm = ref({ name: '', description: '', icon: '', status: '', year: '', techsStr: '', full_description: '', demo_url: '', repo_url: '' })

function openProjectForm(item?: any) {
  editingProject.value = item || null
  projectForm.value = item
    ? { name: item.name || '', description: item.description || '', icon: item.icon || '', status: item.status || '', year: item.year || '', techsStr: (item.techs || []).join(','), full_description: item.full_description || '', demo_url: item.demo_url || '', repo_url: item.repo_url || '' }
    : { name: '', description: '', icon: '', status: '', year: '', techsStr: '', full_description: '', demo_url: '', repo_url: '' }
  showProjectForm.value = true
}

async function saveProject() {
  saving.value = true
  try {
    const payload = { ...projectForm.value, techs: projectForm.value.techsStr.split(',').map((s: string) => s.trim()).filter(Boolean) }
    if (editingProject.value) {
      await adminApi.updateProject(editingProject.value.id, payload)
    } else {
      await adminApi.createProject(payload)
    }
    showProjectForm.value = false
    loadAll()
  } catch (e) { console.error('Failed to save project', e); alert('保存失败，请重试') }
  finally { saving.value = false }
}
async function deleteProject(id: number) {
  if (!confirm('Delete?')) return
  try { await adminApi.deleteProject(id); loadAll() } catch (e) { console.error('Failed to delete project', e); alert('删除失败，请重试') }
}

// Award
const showAwardForm = ref(false)
const editingAward = ref<any>(null)
const awardForm = ref({ title: '', organization: '', award_date: '', level: '' })

function openAwardForm(item?: any) {
  editingAward.value = item || null
  awardForm.value = item
    ? { title: item.title, organization: item.organization, award_date: item.award_date?.toString().slice(0, 10) || '', level: item.level }
    : { title: '', organization: '', award_date: '', level: '' }
  showAwardForm.value = true
}

async function saveAward() {
  saving.value = true
  try {
    const payload = { ...awardForm.value }
    if (editingAward.value) {
      await adminApi.updateAward(editingAward.value.id, payload)
    } else {
      await adminApi.createAward(payload)
    }
    showAwardForm.value = false
    loadAll()
  } catch (e) { console.error('Failed to save award', e); alert('保存失败，请重试') }
  finally { saving.value = false }
}

async function deleteAward(id: number) {
  if (!confirm('Delete?')) return
  try { await adminApi.deleteAward(id); loadAll() } catch (e) { console.error('Failed to delete award', e); alert('删除失败，请重试') }
}

onMounted(() => { if (token.value) { loadAll(); if (activeTab.value === 'rag') loadRag() } })
</script>