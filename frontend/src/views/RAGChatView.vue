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
              <div class="whitespace-pre-wrap text-sm leading-relaxed">{{ msg.content }}</div>
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
  sources?: string[];
  confidence?: number;
}

const messages = ref<Message[]>([]);
const inputText = ref("");
const isStreaming = ref(false);
const selectedKbId = ref("");
const knowledgeBases = ref<{ id: string; name: string }[]>([]);
const messagesContainer = ref<HTMLElement | null>(null);

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
  const assistantMsg: Message = { role: "assistant", content: "" };
  messages.value.push(assistantMsg);

  try {
    const { url, body } = ragApi.queryStreamUrl(trimmed, selectedKbId.value || undefined);
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
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
          if (data === "[DONE]") continue;
          if (data.startsWith("[ERROR]")) {
            assistantMsg.content += `\n⚠️ ${data.slice(7)}`;
          } else {
            assistantMsg.content += data;
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