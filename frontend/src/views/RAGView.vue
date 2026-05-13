<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Hero -->
      <div class="text-center mb-12">
        <div class="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500 p-1 mb-8 glow-border">
          <div class="w-full h-full rounded-xl bg-gray-100 dark:bg-dark-100 flex items-center justify-center">
            <span class="text-6xl">🤖</span>
          </div>
        </div>
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 dark:text-white mb-4">
          AI 知识库
        </h1>
        <p class="text-xl text-gray-500 dark:text-gray-400">
          基于 RAG 技术的智能问答系统 —— 上传文档，构建你的私有知识库
        </p>
      </div>

      <!-- Knowledge Bases -->
      <div class="glass rounded-2xl p-6 mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">我的知识库</h2>
          <button
            @click="showCreateKb = true"
            class="px-4 py-2 bg-primary-500 text-white text-sm font-medium rounded-xl hover:bg-primary-600 transition-colors"
          >
            + 新建知识库
          </button>
        </div>

        <!-- Create KB Form -->
        <div v-if="showCreateKb" class="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-xl">
          <div class="flex gap-3">
            <input
              v-model="newKbName"
              type="text"
              placeholder="知识库名称"
              class="flex-1 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-primary-500"
              @keyup.enter="createKnowledgeBase"
            />
            <input
              v-model="newKbDesc"
              type="text"
              placeholder="描述（可选）"
              class="flex-1 px-3 py-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg text-sm text-gray-900 dark:text-white outline-none focus:ring-2 focus:ring-primary-500"
              @keyup.enter="createKnowledgeBase"
            />
            <button
              @click="createKnowledgeBase"
              :disabled="!newKbName.trim()"
              class="px-4 py-2 bg-green-500 text-white text-sm font-medium rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
            >
              创建
            </button>
            <button
              @click="showCreateKb = false"
              class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 text-sm rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition-colors"
            >
              取消
            </button>
          </div>
        </div>

        <!-- KB List -->
        <div v-if="knowledgeBases.length === 0 && !loading" class="text-center py-8 text-gray-400">
          <p class="mb-2">还没有知识库</p>
          <p class="text-sm">点击"新建知识库"创建你的第一个知识库</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="kb in knowledgeBases"
            :key="kb.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-2">
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ kb.name }}</h3>
                  <span v-if="kb.is_default" class="px-2 py-0.5 text-xs rounded-full bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-300">默认</span>
                </div>
                <p v-if="kb.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ kb.description }}</p>
              </div>
              <div class="flex items-center gap-2">
                <!-- Upload Button -->
                <label
                  :for="'file-upload-' + kb.id"
                  class="px-3 py-1.5 text-xs bg-blue-500 text-white rounded-lg hover:bg-blue-600 cursor-pointer transition-colors"
                >
                  📄 上传文档
                </label>
                <input
                  :id="'file-upload-' + kb.id"
                  type="file"
                  accept=".pdf,.docx,.md,.html,.txt"
                  class="hidden"
                  @change="(e) => handleFileUpload(kb.id, e)"
                />
                <button
                  @click="goToChat(kb.id)"
                  class="px-3 py-1.5 text-xs bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
                >
                  💬 对话
                </button>
                <button
                  @click="deleteKnowledgeBase(kb.id)"
                  class="px-3 py-1.5 text-xs bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                >
                  删除
                </button>
              </div>
            </div>
            <!-- Documents in this KB -->
            <div v-if="kb._documents && kb._documents.length > 0" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
              <p class="text-xs text-gray-400 mb-2">文档列表：</p>
              <div class="space-y-1">
                <div
                  v-for="doc in kb._documents"
                  :key="doc.id"
                  class="flex items-center justify-between text-sm"
                >
                  <span class="text-gray-600 dark:text-gray-300">
                    <span :class="['inline-block w-2 h-2 rounded-full mr-2', doc.status === 'completed' ? 'bg-green-400' : doc.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400']"></span>
                    {{ doc.filename }}
                    <span class="text-xs text-gray-400 ml-2">({{ doc.chunk_count }} chunks)</span>
                  </span>
                  <button
                    @click="deleteDocument(doc.id, kb.id)"
                    class="text-xs text-red-400 hover:text-red-600 transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="glass rounded-xl p-4 text-center hover:-translate-y-1 transition-transform duration-300"
        >
          <div class="text-3xl mb-2">{{ feature.icon }}</div>
          <h3 class="font-semibold text-gray-900 dark:text-white text-sm">{{ feature.title }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ feature.desc }}</p>
        </div>
      </div>

      <!-- CTA -->
      <div class="text-center">
        <router-link
          to="/rag/chat"
          class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 hover:-translate-y-1"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          开始对话
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ragApi } from "@/api";

const router = useRouter();
const knowledgeBases = ref<any[]>([]);
const loading = ref(true);
const showCreateKb = ref(false);
const newKbName = ref("");
const newKbDesc = ref("");

const features = [
  { icon: "📄", title: "多格式解析", desc: "PDF / Word / MD / HTML" },
  { icon: "🔍", title: "语义检索", desc: "BGE-M3 向量 + BM25" },
  { icon: "🎯", title: "智能重排序", desc: "BGE-reranker-v2-m3" },
  { icon: "💬", title: "流式对话", desc: "DeepSeek-V4 + SSE" },
];

onMounted(async () => {
  await loadKnowledgeBases();
  loading.value = false;
});

async function loadKnowledgeBases() {
  try {
    const res: any = await ragApi.getKnowledgeBases();
    if (res.success && res.data) {
      knowledgeBases.value = res.data;
      // Load documents for each KB
      for (const kb of knowledgeBases.value) {
        try {
          const docRes: any = await ragApi.getDocuments(kb.id);
          kb._documents = docRes.success ? docRes.data || [] : [];
        } catch {
          kb._documents = [];
        }
      }
    }
  } catch (e) {
    console.error("Failed to load knowledge bases:", e);
  }
}

async function createKnowledgeBase() {
  if (!newKbName.value.trim()) return;
  try {
    await ragApi.createKnowledgeBase({
      name: newKbName.value.trim(),
      description: newKbDesc.value.trim() || undefined,
    });
    newKbName.value = "";
    newKbDesc.value = "";
    showCreateKb.value = false;
    await loadKnowledgeBases();
  } catch (e) {
    console.error("Failed to create KB:", e);
  }
}

async function deleteKnowledgeBase(kbId: string) {
  if (!confirm("确定删除该知识库及其所有文档？")) return;
  try {
    await ragApi.deleteKnowledgeBase(kbId);
    await loadKnowledgeBases();
  } catch (e) {
    console.error("Failed to delete KB:", e);
  }
}

async function handleFileUpload(kbId: string, event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;

  try {
    await ragApi.uploadDocument(kbId, file);
    await loadKnowledgeBases();
  } catch (e) {
    console.error("Failed to upload:", e);
    alert("上传失败，请重试");
  } finally {
    input.value = "";
  }
}

async function deleteDocument(docId: string, kbId: string) {
  if (!confirm("确定删除该文档？")) return;
  try {
    await ragApi.deleteDocument(docId);
    await loadKnowledgeBases();
  } catch (e) {
    console.error("Failed to delete document:", e);
  }
}

function goToChat(kbId: string) {
  router.push({ path: "/rag/chat", query: { kb: kbId } });
}
</script>