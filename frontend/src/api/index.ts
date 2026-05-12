/**
 * API 客户端封装
 *
 * 基于 Axios 实例，统一配置 baseURL、超时和响应拦截。
 * 按业务模块拆分为 blogApi、projectApi、ragApi 三个子对象。
 *
 * 所有列表请求支持分页参数（page/page_size）。
 */

import axios from "axios";

// 创建 Axios 实例，所有请求以 /api 为基础路径
const api = axios.create({
  baseURL: "/api",
  timeout: 10000, // 10 秒超时
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

/** RAG API（待二期实现） */
export const ragApi = {
  query: (question: string) => api.post("/rag/query", { question }),
  getKnowledgeBases: () => api.get("/rag/knowledge-bases"),
  createKnowledgeBase: (data: any) => api.post("/rag/knowledge-bases", data),
  deleteKnowledgeBase: (id: string) =>
    api.delete(`/rag/knowledge-bases/${id}`),
};

export default api;
