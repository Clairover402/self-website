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

        <div class="flex space-x-2 mb-8">
          <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key" :class="activeTab === tab.key ? clsActive : clsInactive">{{ tab.label }}</button>
        </div>

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

        <div v-if="activeTab === 'contacts'" class="space-y-4">
          <div v-for="item in contactList" :key="item.id" class="glass rounded-xl p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-gray-900 dark:text-white font-medium">{{ item.name }}</span>
              <span class="text-gray-500 dark:text-gray-400 text-sm">{{ formatDate(item.created_at) }}</span>
            </div>
            <p class="text-gray-500 dark:text-gray-400 text-sm mb-1">{{ item.email }}</p>
            <p class="text-gray-600 dark:text-gray-300 text-sm">{{ item.message }}</p>
          </div>
        </div>

        <!-- Blog Modal -->
        <div v-if="showBlogForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="showBlogForm = false">
          <div class="glass rounded-2xl p-6 w-full max-w-lg mx-4 max-h-80vh overflow-y-auto">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingBlog ? 'Edit Blog' : 'New Blog' }}</h3>
            <div class="space-y-3">
              <input v-model="blogForm.title" placeholder="Title" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="blogForm.slug" placeholder="slug" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="blogForm.excerpt" placeholder="Excerpt" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <textarea v-model="blogForm.content" rows="8" placeholder="Content (Markdown)" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm resize-none"></textarea>
              <input v-model="blogForm.cover" placeholder="Cover emoji" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="blogForm.tagsStr" placeholder="Tags (comma separated)" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showBlogForm = false" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white">Cancel</button>
              <button @click="saveBlog" :disabled="saving" class="px-4 py-2 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
            </div>
          </div>
        </div>

        <!-- Project Modal -->
        <div v-if="showProjectForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="showProjectForm = false">
          <div class="glass rounded-2xl p-6 w-full max-w-lg mx-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingProject ? 'Edit Project' : 'New Project' }}</h3>
            <div class="space-y-3">
              <input v-model="projectForm.name" placeholder="Name" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="projectForm.description" placeholder="Description" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="projectForm.icon" placeholder="Icon emoji" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="projectForm.status" placeholder="Status" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="projectForm.techsStr" placeholder="Techs (comma separated)" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
            </div>
            <div class="flex justify-end space-x-3 mt-6">
              <button @click="showProjectForm = false" class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white">Cancel</button>
              <button @click="saveProject" :disabled="saving" class="px-4 py-2 text-sm bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50">{{ saving ? 'Saving...' : 'Save' }}</button>
            </div>
          </div>
        </div>

        <!-- Award Modal -->
        <div v-if="showAwardForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="showAwardForm = false">
          <div class="glass rounded-2xl p-6 w-full max-w-lg mx-4">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">{{ editingAward ? 'Edit Award' : 'New Award' }}</h3>
            <div class="space-y-3">
              <input v-model="awardForm.title" placeholder="Title" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="awardForm.organization" placeholder="Organization" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <input v-model="awardForm.award_date" type="date" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:border-primary-500 text-sm" />
              <select v-model="awardForm.level" class="w-full px-3 py-2 bg-white border border-gray-200 dark:bg-white/5 dark:border-white/10 rounded-lg text-gray-900 dark:text-white focus:outline-none focus:border-primary-500 text-sm">
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

const clsActive = 'px-4 py-2 rounded-lg text-sm bg-primary-500 text-white transition-colors'
const clsInactive = 'px-4 py-2 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white glass transition-colors'

const tabs = [
  { key: 'blogs', label: 'Blogs' },
  { key: 'projects', label: 'Projects' },
  { key: 'awards', label: 'Awards' },
  { key: 'contacts', label: 'Contacts' },
]

const blogList = ref<any[]>([])
const projectList = ref<any[]>([])
const awardList = ref<any[]>([])
const contactList = ref<any[]>([])

function formatDate(d: string) { return d ? new Date(d).toISOString().slice(0, 10) : '' }
function getHeaders() { return { Authorization: 'Bearer ' + token.value } }
function logout() { token.value = ''; localStorage.removeItem('admin_token') }

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
function openAwardForm(_item?: any) { /* TODO */ }
async function deleteAward(id: number) {
  if (!confirm('Delete?')) return
  try { await axios.delete('/api/admin/awards/' + id, { headers: getHeaders() }); loadAll() } catch {}
}

onMounted(() => { if (token.value) loadAll() })
</script>
