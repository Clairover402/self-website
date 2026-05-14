/**
 * API 客户端封装
 *
 * 基于 Axios 实例，统一配置 baseURL、超时和响应拦截。
 * 按业务模块拆分为 blogApi、projectApi、awardApi、ragApi、adminRagApi 五个子对象。
 *
 * 所有列表请求支持分页参数（page/page_size）。
 */

import axios from "axios";

// 创建 Axios 实例，所有请求以 /api 为基础路径
const api = axios.create({
  baseURL: "/api",
  timeout: 30000, // RAG 查询可能较慢，延长到 30 秒
});

// 响应拦截器：自动解包 axios response，直接返回 data 层
// 前端拿到的就是后端的 Result[T] 结构
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

/** 分页请求参数（后端查询参数名一致） */
export interface PaginationParams {
  page?: number;
  page_size?: number;
}

/** 博客 API */
export const blogApi = {
  /**
   * 获取博客列表（分页 + 搜索 + 标签过滤）
   * @param params - page、page_size、search、tag 均为可选
   */
  getList: (params: PaginationParams & { search?: string; tag?: string } = {}) =>
    api.get("/blogs", { params }),

  /** 根据 slug 获取博客详情 */
  getBySlug: (slug: string) => api.get(`/blogs/${slug}`),
};

/** 项目 API */
export const projectApi = {
  /**
   * 获取项目列表（分页 + 搜索 + 状态过滤 + 技术栈过滤）
   * @param params - page、page_size、search、status、tech 均为可选
   */
  getList: (
    params: PaginationParams & {
      search?: string;
      status?: string;
      tech?: string;
    } = {}
  ) => api.get("/projects", { params }),

  /** 根据 ID 获取项目详情 */
  getById: (id: string) => api.get(`/projects/${id}`),
};

/** 奖项 API */
export const awardApi = {
  getList: (params: PaginationParams & { search?: string; level?: string } = {}) =>
    api.get("/awards", { params }),
  getById: (id: string) => api.get(`/awards/${id}`),
};

/** RAG 公开 API（仅聊天查询和只读列表） */
export const ragApi = {
  /** RAG 查询（非流式） */
  query: (question: string, knowledge_base_id?: string) =>
    api.post("/rag/query", { question, knowledge_base_id }),

  /** RAG 流式查询（返回 fetch 配置，由调用方用 ReadableStream 消费） */
  queryStreamUrl: (question: string, knowledge_base_id?: string) => {
    return { url: "/api/rag/query/stream", body: { question, knowledge_base_id } };
  },

  /** 知识库列表（只读，供聊天选择知识库） */
  getKnowledgeBases: () => api.get("/rag/knowledge-bases"),

  /** 对话记录 */
  getConversations: (kb_id?: string) =>
    api.get("/rag/conversations", { params: kb_id ? { kb_id } : {} }),
};

/** RAG 管理后台 API（JWT 保护，需在请求头中带 Authorization: Bearer <token>） */
export const adminRagApi = {
  /** 知识库 CRUD */
  getKnowledgeBases: () => api.get("/admin/rag/knowledge-bases"),
  getKnowledgeBase: (id: string) => api.get(`/admin/rag/knowledge-bases/${id}`),
  createKnowledgeBase: (data: { name: string; description?: string; is_default?: boolean }) =>
    api.post("/admin/rag/knowledge-bases", data),
  updateKnowledgeBase: (id: string, data: { name?: string; description?: string; is_default?: boolean }) =>
    api.put(`/admin/rag/knowledge-bases/${id}`, data),
  deleteKnowledgeBase: (id: string) =>
    api.delete(`/admin/rag/knowledge-bases/${id}`),

  /** 文档管理 */
  getDocuments: (kb_id?: string) =>
    api.get("/admin/rag/documents", { params: kb_id ? { kb_id } : {} }),
  uploadDocument: (kb_id: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post(`/admin/rag/documents?kb_id=${encodeURIComponent(kb_id)}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  deleteDocument: (doc_id: string) =>
    api.delete(`/admin/rag/documents/${doc_id}`),
};

export default api;
