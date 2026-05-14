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
              <label class="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 cursor-pointer">
                <input v-model="newKbDefault" type="checkbox" class="rounded" /> 默认
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
              <textarea v-model="blogForm.content" placeholder="Content (Markdown)" rows="12" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none font-mono"></textarea>
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
              <input v-model="awardForm.date" type="date" class="w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none" />
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
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

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
const expandedKb = ref<string | null>(null)

function formatDate(d: string) { return d ? new Date(d).toISOString().slice(0, 10) : '' }
function getHeaders() { return { Authorization: 'Bearer ' + token.value } }
function logout() { token.value = ''; localStorage.removeItem('admin_token') }

function switchTab(key: string) {
  activeTab.value = key
  if (key === 'rag') loadRag()
}

async function doLogin() {
  loginLoading.value = true
  loginError.value = ''
  try {
    const res: any = await axios.post('/api/admin/login', { password: password.value })
    if (res.data?.success && res.data?.data?.token) {
      token.value = res.data.data.token
      localStorage.setItem('admin_token', token.value)
      loadAll()
    } else { loginError.value = 'Invalid password' }
  } catch { loginError.value = 'Login failed' }
  finally { loginLoading.value = false }
}

async function loadAll() {
  try {
    const [b, p, a, c] = await Promise.all([
      axios.get('/api/blogs?page_size=100'),
      axios.get('/api/projects?page_size=100'),
      axios.get('/api/awards?page_size=100'),
      axios.get('/api/admin/contacts', { headers: getHeaders() }),
    ])
    blogList.value = (b.data as any)?.data?.items || []
    projectList.value = (p.data as any)?.data?.items || []
    awardList.value = (a.data as any)?.data?.items || []
    contactList.value = (c.data as any)?.data || []
  } catch {}
}

// ===== RAG =====

async function loadRag() {
  ragLoading.value = true
  try {
    const res: any = await axios.get('/api/admin/rag/knowledge-bases', { headers: getHeaders() })
    kbList.value = res.data?.data || []
    // Load documents for each KB
    for (const kb of kbList.value) {
      try {
        const docRes: any = await axios.get(`/api/admin/rag/documents?kb_id=${encodeURIComponent(kb.id)}`, { headers: getHeaders() })
        kb._documents = docRes.data?.data || []
      } catch { kb._documents = [] }
    }
  } catch (e) { console.error('Failed to load RAG data', e) }
  finally { ragLoading.value = false }
}

async function createKb() {
  if (!newKbName.value.trim()) return
  try {
    await axios.post('/api/admin/rag/knowledge-bases', {
      name: newKbName.value.trim(),
      description: newKbDesc.value.trim() || undefined,
      is_default: newKbDefault.value,
    }, { headers: getHeaders() })
    newKbName.value = ''
    newKbDesc.value = ''
    newKbDefault.value = false
    await loadRag()
  } catch (e) { console.error('Failed to create KB', e) }
}

async function deleteKb(kbId: string) {
  if (!confirm('确定删除该知识库及其所有文档？')) return
  try {
    await axios.delete(`/api/admin/rag/knowledge-bases/${encodeURIComponent(kbId)}`, { headers: getHeaders() })
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
    const formData = new FormData()
    formData.append('file', file)
    await axios.post(`/api/admin/rag/documents?kb_id=${encodeURIComponent(kbId)}`, formData, {
      headers: { ...getHeaders(), 'Content-Type': 'multipart/form-data' },
    })
    await loadRag()
  } catch (e) { console.error('Upload failed', e); alert('上传失败，请重试') }
  finally { input.value = '' }
}

async function deleteDoc(docId: string, _kbId: string) {
  if (!confirm('确定删除该文档？')) return
  try {
    await axios.delete(`/api/admin/rag/documents/${encodeURIComponent(docId)}`, { headers: getHeaders() })
    await loadRag()
  } catch (e) { console.error('Failed to delete doc', e) }
}

// Blog
const showBlogForm = ref(false)
const editingBlog = ref<any>(null)
const blogForm = ref({ title: '', slug: '', excerpt: '', content: '', cover: '', tagsStr: '' })

function openBlogForm(item?: any) {
  editingBlog.value = item || null
  blogForm.value = item
    ? { title: item.title, slug: item.slug, excerpt: item.excerpt, content: item.content, cover: item.cover || '', tagsStr: (item.tags || []).join(',') }
    : { title: '', slug: '', excerpt: '', content: '', cover: '', tagsStr: '' }
  showBlogForm.value = true
}

async function saveBlog() {
  saving.value = true
  try {
    const payload = { ...blogForm.value, tags: blogForm.value.tagsStr.split(',').map((s: string) => s.trim()).filter(Boolean), read_time: 5 }
    if (editingBlog.value) {
      await axios.put('/api/admin/blogs/' + editingBlog.value.slug, payload, { headers: getHeaders() })
    } else {
      await axios.post('/api/admin/blogs', payload, { headers: getHeaders() })
    }
    showBlogForm.value = false
    loadAll()
  } catch {}
  finally { saving.value = false }
}

async function deleteBlog(slug: string) {
  if (!confirm('Delete?')) return
  try { await axios.delete('/api/admin/blogs/' + slug, { headers: getHeaders() }); loadAll() } catch {}
}

// Project
function openProjectForm(_item?: any) { /* TODO */ }
async function deleteProject(id: number) {
  if (!confirm('Delete?')) return
  try { await axios.delete('/api/admin/projects/' + id, { headers: getHeaders() }); loadAll() } catch {}
}

// Award
const showAwardForm = ref(false)
const editingAward = ref<any>(null)
const awardForm = ref({ title: '', organization: '', date: '', level: '' })

function openAwardForm(item?: any) {
  editingAward.value = item || null
  awardForm.value = item
    ? { title: item.title, organization: item.organization, date: item.date?.slice(0, 10) || '', level: item.level }
    : { title: '', organization: '', date: '', level: '' }
  showAwardForm.value = true
}

async function saveAward() {
  saving.value = true
  try {
    const payload = { ...awardForm.value }
    if (editingAward.value) {
      await axios.put(`/api/admin/awards/${editingAward.value.id}`, payload, { headers: getHeaders() })
    } else {
      await axios.post('/api/admin/awards', payload, { headers: getHeaders() })
    }
    showAwardForm.value = false
    loadAll()
  } catch {}
  finally { saving.value = false }
}

async function deleteAward(id: number) {
  if (!confirm('Delete?')) return
  try { await axios.delete('/api/admin/awards/' + id, { headers: getHeaders() }); loadAll() } catch {}
}

onMounted(() => { if (token.value) { loadAll(); if (activeTab.value === 'rag') loadRag() } })
</script>
