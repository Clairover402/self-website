"""
=============================================================================
RAG Query Rewriter — LLM 驱动的查询改写
=============================================================================

在检索前对用户问题进行改写优化，提升检索召回质量。
支持三种策略（通过 QUERY_REWRITE_STRATEGY 配置）：
  - simple: 单轮优化，补充关键词、消除歧义
  - multi:  生成多条变体查询，分别检索后合并
  - hyde:   先生成假设答案，用答案做检索查询

位置：embed_query() 之前
"""

from dataclasses import dataclass, field
from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import settings


@dataclass
class RewrittenQuery:
    """改写结果：search_queries 用于检索，original 用于最终生成"""
    search_queries: List[str] = field(default_factory=list)
    original: str = ""


class QueryRewriter:
    """LLM 驱动的查询改写器"""

    def __init__(self):
        self._llm: ChatOpenAI | None = None

    @property
    def llm(self) -> ChatOpenAI:
        """延迟初始化 LLM 客户端（与 QueryPipeline 共用 API）"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model="deepseek-chat",
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=0.1,      # 低温度确保改写稳定
                max_tokens=256,       # 改写通常很短
            )
        return self._llm

    # =====================================================================
    # 公共入口
    # =====================================================================

    def rewrite(self, question: str) -> RewrittenQuery:
        """
        按配置策略改写用户问题。

        异常时回退：返回原始问题，不影响主流程。
        """
        if not settings.QUERY_REWRITE_ENABLED:
            return RewrittenQuery(search_queries=[question], original=question)

        strategy = settings.QUERY_REWRITE_STRATEGY
        try:
            if strategy == "multi":
                queries = self._rewrite_multi(question)
            elif strategy == "hyde":
                queries = self._rewrite_hyde(question)
            else:
                queries = self._rewrite_simple(question)

            # 确保至少有一条查询
            if not queries:
                queries = [question]

            return RewrittenQuery(search_queries=queries, original=question)
        except Exception:
            # LLM 不可用时回退到原始问题
            return RewrittenQuery(search_queries=[question], original=question)

    # =====================================================================
    # 策略实现
    # =====================================================================

    def _rewrite_simple(self, question: str) -> List[str]:
        """
        单轮优化：补充关键词、消除歧义、规范术语。

        Prompt 设计要点：
        - 要求输出纯查询文本，不要解释
        - 引导 LLM 补充同义词和相关术语
        - 对模糊指代（"那个"、"这个"）进行实体替换
        """
        system = (
            "你是一个搜索查询优化器。你的任务是将用户问题改写为更适合知识库检索的查询语句。"
            "规则：\n"
            "1. 补充缺失的关键词和同义词\n"
            "2. 将模糊指代（"那个"、"这个"、"它"）替换为具体实体\n"
            "3. 使用规范的技术术语\n"
            "4. 只输出改写后的查询，不要任何解释\n"
            "5. 保留原问题的核心意图"
        )
        user = f"用户问题：{question}\n\n优化后的查询："
        result = self._call_llm(system, user)
        return [result.strip()] if result.strip() else [question]

    def _rewrite_multi(self, question: str) -> List[str]:
        """
        多查询生成：从不同角度生成 3~4 条变体查询。

        用途：单个查询可能遗漏不同表述的文档，多条查询
        分别检索后合并结果，提高召回覆盖率。
        """
        system = (
            "你是一个搜索查询扩展器。从不同角度生成多个查询变体以提高检索召回率。"
            "规则：\n"
            "1. 生成 3~4 条不同的查询\n"
            "2. 每条查询从不同角度或用不同措辞表达同一个问题\n"
            "3. 包含关键词查询和自然语言查询\n"
            "4. 每行一条查询，不要编号，不要任何解释"
        )
        user = f"用户问题：{question}\n\n查询变体："
        result = self._call_llm(system, user)

        # 按行解析，过滤空行
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        return lines[:4] if lines else [question]

    def _rewrite_hyde(self, question: str) -> List[str]:
        """
        HyDE (Hypothetical Document Embeddings)：
        先生成一段假设的答案，用答案文本做检索查询。

        原理：答案文本包含的术语和句式与真实文档更接近，
        向量检索时更容易命中相关内容。

        截取前 200 字避免过长。
        """
        system = (
            "你是一个知识渊博的助手。请用一段话（100-200字）回答用户的问题。"
            "即使你不确定答案，也请基于常识给出一个合理的回答。"
            "只输出回答内容，不要任何解释。"
        )
        user = f"问题：{question}\n\n回答："
        result = self._call_llm(system, user)
        # 截取前 300 字符作为检索查询
        return [result.strip()[:300]] if result.strip() else [question]

    # =====================================================================
    # 内部方法
    # =====================================================================

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM 并返回文本内容"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
