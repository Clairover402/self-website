import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const blogApi = {
  getList: () => api.get('/blogs'),
  getBySlug: (slug: string) => api.get(`/blogs/${slug}`)
}

export const projectApi = {
  getList: () => api.get('/projects'),
  getById: (id: string) => api.get(`/projects/${id}`)
}

export const ragApi = {
  query: (question: string) => api.post('/rag/query', { question }),
  getKnowledgeBases: () => api.get('/rag/knowledge-bases'),
  createKnowledgeBase: (data: any) => api.post('/rag/knowledge-bases', data),
  deleteKnowledgeBase: (id: string) => api.delete(`/rag/knowledge-bases/${id}`)
}

export default api
