<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <header class="text-center mb-8">
        <router-link
          to="/rag"
          class="inline-flex items-center text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-white transition-colors duration-200 mb-6"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          返回 AI 知识库
        </router-link>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">智能对话</h1>
        <p class="text-gray-500 dark:text-gray-400">基于 RAG 的智能问答系统</p>
      </header>

      <!-- Toast notifications -->
      <div
        v-if="toast.show"
        :class="[
          'fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-lg text-sm font-medium transition-all duration-300',
          toast.type === 'error' ? 'bg-red-500 text-white' : 'bg-yellow-500 text-white'
        ]"
      >
        {{ toast.message }}
      </div>

      <!-- KB Selector -->
      <div class="mb-4 flex items-center gap-3">
        <label class="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">知识库：</label>
        <select
          v-model="selectedKbId"
          class="flex-1 max-w-xs px-3 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
        >
          <option value="">全部知识库</option>
          <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb.id">
            {{ kb.name }}
          </option>
        </select>
        <span v-if="knowledgeBases.length === 0" class="text-xs text-gray-400">暂无知识库</span>
      </div>

      <!-- Chat Area -->
      <div
        ref="chatContainer"
        class="glass rounded-2xl overflow-hidden flex flex-col"
        style="height: calc(100vh - 340px); min-height: 400px;"
      >
        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
          <div v-if="messages.length === 0" class="flex items-center justify-center h-full">
            <div class="text-center text-gray-400 dark:text-gray-500">
              <div class="w-16 h-16 mx-auto rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-4">
                <span class="text-3xl">🤖</span>
              </div>
              <p>输入问题开始对话</p>
              <div class="mt-4 flex flex-wrap gap-2 justify-center">
                <button
                  v-for="q in quickQuestions"
                  :key="q"
                  @click="sendMessage(q)"
                  class="px-3 py-1.5 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-colors"
                >
                  {{ q }}
                </button>
              </div>
            </div>
          </div>

          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
          >
            <div
              :class="[
                'max-w-[80%] rounded-2xl px-4 py-3',
                msg.role === 'user'
                  ? 'bg-primary-500 text-white rounded-br-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md'
              ]"
            >
              <div v-if="msg.thinking" class="text-xs opacity-60 mb-1 animate-pulse">搜索中...</div><div class="whitespace-pre-wrap text-sm leading-relaxed">{{ msg.content }}</div>
              <!-- Evaluate -->
              <div v-if="msg.role === 'assistant' && msg.content && msg.content.length > 10" class="mt-2 pt-2 border-t border-white/10">
                <div v-if="!msg.evalResult && !msg.evaluating">
                  <button
                    @click="evaluateMessage(i)"
                    class="text-xs px-2 py-1 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                  >
                    📊 评估
                  </button>
                </div>
                <div v-if="msg.evaluating" class="text-xs opacity-70">
                  ⏳ 评估中...
                </div>
                <div v-if="msg.evalResult" class="mt-2 space-y-1">
                  <!-- Ground truth input -->
                  <div v-if="!msg.evalDone" class="flex gap-2 mb-2">
                    <input
                      v-model="msg.groundTruth"
                      type="text"
                      placeholder="参考答案（可选，填了出4项指标）"
                      class="flex-1 px-2 py-1 text-xs rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40"
                    />
                    <button @click="runEvaluate(i)" class="text-xs px-3 py-1 rounded-lg bg-white/20 hover:bg-white/30 transition-colors">
                      开始
                    </button>
                  </div>
                  <!-- Results -->
                  <div v-if="msg.evalDone" class="space-y-1">
                    <div class="flex items-center gap-2 text-xs">
                      <span class="w-24 opacity-70">忠实度</span>
                      <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div class="h-full bg-green-400 rounded-full" :style="{ width: (msg.evalResult.faithfulness * 100) + '%' }"></div>
                      </div>
                      <span class="w-10 text-right">{{ (msg.evalResult.faithfulness * 100).toFixed(0) }}%</span>
                    </div>
                    <div class="flex items-center gap-2 text-xs">
                      <span class="w-24 opacity-70">答案相关性</span>
                      <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div class="h-full bg-blue-400 rounded-full" :style="{ width: (msg.evalResult.answer_relevancy * 100) + '%' }"></div>
                      </div>
                      <span class="w-10 text-right">{{ (msg.evalResult.answer_relevancy * 100).toFixed(0) }}%</span>
                    </div>
                    <div v-if="msg.evalResult.context_precision != null" class="flex items-center gap-2 text-xs">
                      <span class="w-24 opacity-70">上下文精度</span>
                      <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div class="h-full bg-purple-400 rounded-full" :style="{ width: (msg.evalResult.context_precision * 100) + '%' }"></div>
                      </div>
                      <span class="w-10 text-right">{{ (msg.evalResult.context_precision * 100).toFixed(0) }}%</span>
                    </div>
                    <div v-if="msg.evalResult.context_recall != null" class="flex items-center gap-2 text-xs">
                      <span class="w-24 opacity-70">上下文召回率</span>
                      <div class="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div class="h-full bg-orange-400 rounded-full" :style="{ width: (msg.evalResult.context_recall * 100) + '%' }"></div>
                      </div>
                      <span class="w-10 text-right">{{ (msg.evalResult.context_recall * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                </div>
              </div>
              <!-- Sources -->
              <div v-if="msg.sources && msg.sources.length > 0" class="mt-2 pt-2 border-t border-white/20">
                <p class="text-xs opacity-70 mb-1">📚 参考来源：</p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="(src, si) in msg.sources.slice(0, 5)"
                    :key="si"
                    class="px-2 py-0.5 text-xs rounded-full bg-white/20"
                  >
                    {{ src }}
                  </span>
                </div>
              </div>
              <!-- Confidence -->
              <div v-if="msg.confidence > 0" class="mt-1 text-xs opacity-60">
                置信度：{{ (msg.confidence * 100).toFixed(0) }}%
              </div>
            </div>
          </div>

          <!-- Streaming indicator -->
          <div v-if="isStreaming" class="flex justify-start">
            <div class="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex space-x-1">
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-4 border-t border-gray-200 dark:border-gray-700">
          <form @submit.prevent="sendMessage(inputText)" class="flex gap-2">
            <input
              v-model="inputText"
              type="text"
              placeholder="输入你的问题..."
              :disabled="isStreaming"
              class="flex-1 px-4 py-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              :disabled="isStreaming || !inputText.trim()"
              class="px-6 py-3 bg-gradient-to-r from-primary-500 to-primary-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-primary-500/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="!isStreaming" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
              <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from "vue";
import { ragApi } from "@/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  thinking?: boolean;
  sources?: string[];
  confidence?: number;
  evalResult?: any;
  evaluating?: boolean;
  groundTruth?: string;
  evalDone?: boolean;
}

const messages = ref<Message[]>([]);
const inputText = ref("");
const isStreaming = ref(false);
const selectedKbId = ref("");
const knowledgeBases = ref<{ id: string; name: string }[]>([]);
const messagesContainer = ref<HTMLElement | null>(null);
const toast = ref<{ show: boolean; message: string; type: string }>({
  show: false,
  message: "",
  type: "error",
});

function showToast(message: string, type: string = "error") {
  toast.value = { show: true, message, type };
  setTimeout(() => {
    toast.value.show = false;
  }, 4000);
}

const quickQuestions = [
  "介绍一下你自己",
  "这个网站有哪些功能？",
  "什么是 RAG 技术？",
];

onMounted(async () => {
  try {
    const res: any = await ragApi.getKnowledgeBases();
    if (res.success && res.data) {
      knowledgeBases.value = res.data;
    }
  } catch (e) {
    console.error("Failed to load knowledge bases:", e);
  }
});

async function evaluateMessage(index: number) {
  const msg = messages.value[index];
  if (!msg || msg.role !== "assistant") return;
  msg.evalResult = {};
  msg.evaluating = false;
  msg.evalDone = false;
  msg.groundTruth = "";
  // Show the ground truth input first
  messages.value[index] = { ...msg, evalResult: {} };
}

async function runEvaluate(index: number) {
  const msg = messages.value[index];
  if (!msg) return;
  msg.evaluating = true;
  messages.value[index] = { ...msg };

  try {
    // Find the corresponding user question
    let userQuestion = "";
    for (let i = index - 1; i >= 0; i--) {
      if (messages.value[i].role === "user") {
        userQuestion = messages.value[i].content;
        break;
      }
    }

    const res: any = await ragApi.evaluate(
      userQuestion || "",
      selectedKbId.value || undefined,
      msg.groundTruth || undefined
    );

    if (res.success) {
      msg.evalResult = res.data;
      msg.evalDone = true;
    } else {
      showToast(res.errorMsg || "评估失败");
    }
  } catch (e: any) {
    showToast(`评估失败: ${e.message || e}`);
    msg.evalResult = null;
  } finally {
    msg.evaluating = false;
    messages.value[index] = { ...msg };
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

async function sendMessage(text: string) {
  const trimmed = text.trim();
  if (!trimmed || isStreaming.value) return;

  inputText.value = "";
  messages.value.push({ role: "user", content: trimmed });
  scrollToBottom();

  isStreaming.value = true;
  const assistantMsg: Message = { role: "assistant", content: "", thinking: true };
  messages.value.push(assistantMsg);

  try {
    const { url, body } = ragApi.queryStreamUrl(trimmed, selectedKbId.value || undefined);
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      if (response.status === 429) {
        assistantMsg.content = "系统繁忙，请稍后再试";
        showToast("系统繁忙，请稍后再试", "warning");
        return;
      }
      if (response.status === 503) {
        assistantMsg.content = "AI 服务暂时不可用（DeepSeek API 异常），请稍后再试或检查日志";
        showToast("AI 服务暂时不可用，请稍后再试或检查日志", "error");
        return;
      }
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error("No response body");

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[THINKING]正在检索知识库...") { assistantMsg.thinking = true; continue; }
          
          if (data === "[DONE]") continue;
          if (data.startsWith("[ERROR]")) {
            assistantMsg.content += `\n⚠️ ${data.slice(7)}`;
          } else {
            assistantMsg.thinking = false; assistantMsg.content += data;
          }
          scrollToBottom();
        }
      }
    }
  } catch (e: any) {
    assistantMsg.content = `抱歉，请求失败：${e.message}`;
  } finally {
    isStreaming.value = false;
    scrollToBottom();
  }
}
</script>