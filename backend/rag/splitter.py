"""
=============================================================================
RAG 核心模块 — 文本切分器 (Text Splitter)
=============================================================================

【RAG 概念入门】
清洗后的文档可能很长（几百页 PDF），不能直接塞给 Embedding 模型——
模型有最大输入长度限制（BGE-M3 最多 8192 token）。
所以要把长文档切成小片段（chunk），每个 chunk 独立做向量化。

【为什么切分是最关键的步骤之一】
- 切太大：超出模型限制，或语义被稀释（一个向量代表太多内容）
- 切太小：丢失上下文，一句话被切断后语义不完整
- 好切分：每个 chunk 是一个完整的"语义单元"

类比数据库分页：
    SELECT * FROM document_pages ORDER BY page LIMIT 500 OFFSET 50;
这里切分器也在做"分页"，但不是按字数，而是按语义边界。

【RecursiveCharacterTextSplitter 的原理】
递归地按优先级尝试分隔符：
1. 先尝试按段落分隔（\n\n）
2. 如果段落还太长，按换行分隔（\n）
3. 如果还太长，按句子分隔（。或.）
4. 最后按空格甚至单字符切分

这样确保 chunk 尽可能在自然的语义边界上断开，而非生硬截断。
"""

from typing import List

# LangChain 的文本切分器，工业级实现
# 相当于 Java 中的 Guava Splitter，但考虑了语义边界
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import settings


class TextSplitter:
    """
    LangChain 递归文本切分器封装。

    【核心参数解释】

    chunk_size (默认 500)：每个 chunk 的目标大小（字符数，非 token 数）
        - 为什么是 500 字符？
          中文一个字≈1.5 个 token，500 字≈750 token。
          BGE-M3 最大 8192 token，LLM 上下文窗口更大。
          500 字约 3~4 段，是合适的"完整语义单元"。
        - 类比 MySQL 的 VARCHAR(500) —— 控制每行数据的大小。

    chunk_overlap (默认 50)：相邻 chunk 之间的重叠字符数
        - 为什么需要重叠？
          防止关键信息刚好卡在两个 chunk 的边界上被"切断"。
          例如："...因此，我们得出结论：" [切分边界] "Python 是最佳选择。"
          前半段在 chunk1，后半段在 chunk2，但谁都不知道"结论"是什么。
          overlap 让 chunk1 末尾和 chunk2 开头有 50 字重叠，
          这样 chunk2 的开头还包括"我们得出结论：Python 是最佳选择"。

    separators：分隔符优先级列表
        ["\n\n", "\n", "。", ".", " ", ""]
        从粗到细：先尝试段落 → 换行 → 中文句号 → 英文句号 → 空格 → 硬切
        注意中文句号（。）排在英文句号（.）前面，因为这是中文文档。
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self._splitter = RecursiveCharacterTextSplitter(
            # 允许外部覆盖配置，否则用 .env 中的默认值
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=chunk_overlap or settings.CHUNK_OVERLAP,
            # 分隔符优先级：越靠前越优先
            separators=["\n\n", "\n", "。", ".", " ", ""],
            # 用字符数（而非 token 数）计算长度，简单直观
            length_function=len,
        )

    def split(self, text: str) -> List[str]:
        """
        将长文本切分为 chunk 列表。

        输入：一篇 5000 字的清洗后文档
        输出：约 10~12 个 chunk，每个约 500 字

        【切分后的数据流】
        split() → embed_documents(chunks) → Qdrant store
        每个 chunk 会独立成为一个向量存在 Qdrant 中。
        """
        return self._splitter.split_text(text)