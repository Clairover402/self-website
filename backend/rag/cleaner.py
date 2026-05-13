"""
=============================================================================
RAG 核心模块 — 文档清洗器 (Document Cleaner)
=============================================================================

【RAG 概念入门】
解析出来的文本通常带有各种"噪音"：HTML 标签残留、多余的空白行、
控制字符、URL 链接等。这些噪音会：
1. 浪费 LLM 的 token（很贵！）
2. 降低检索精度（无关字符干扰向量相似度计算）
3. 让生成的答案中含有垃圾信息

Cleaner = 文本的"洗衣机"，把脏文本洗干净再做后续处理。

【类比 ETL 流程】
整个 Ingest 管线就是一个 ETL（Extract-Transform-Load）：
- Extract（抽取）= Parser 解析
- Transform（转换）= Cleaner 清洗 + Splitter 切分
- Load（加载）= Embedding + Qdrant 存储

在数据仓库中（如 MySQL → Hive），ETL 的第一步也是数据清洗。
=============================================================================
"""

import re


class DocumentCleaner:
    """
    文本清洗器 —— 流水线模式（Pipeline Pattern）

    每个清洗步骤是独立的静态方法，clean() 按固定顺序串联调用。
    类似 Java Stream 的链式调用：
        text.stripTags().removeUrls().normalize().trim()

    全用 @staticmethod 因为清洗是纯函数（无状态）：
    同样的输入永远产生同样的输出，不依赖外部状态。
    """

    @staticmethod
    def clean(text: str) -> str:
        """
        执行全部清洗步骤（按顺序）。

        清洗顺序有讲究：
        1. 先去掉 HTML（结构噪音）
        2. 去掉 URL（内容噪音）
        3. 去掉控制字符（不可见字符）
        4. 规范化空白（合并空格、统一换行）
        5. 去掉空行（美化）

        最后 strip() 去掉首尾空白。
        """
        text = DocumentCleaner._remove_html_tags(text)
        text = DocumentCleaner._remove_urls(text)
        text = DocumentCleaner._remove_control_chars(text)
        text = DocumentCleaner._normalize_whitespace(text)
        text = DocumentCleaner._remove_empty_lines(text)
        return text.strip()

    # =========================================================================
    # 各清洗步骤
    # =========================================================================

    @staticmethod
    def _remove_html_tags(text: str) -> str:
        """
        去除残留 HTML 标签。

        正则 <[^>]+> 的含义：
        <     匹配左尖括号
        [^>]+ 匹配一个或多个非右尖括号的字符
        >     匹配右尖括号
        合起来匹配任何 HTML 标签，如 <div>、<br/>、<span class="foo">

        注意：这里不去除 HTML 实体（如 &amp; &lt; 等），
        因为 Modern 的解析器（BeautifulSoup）已经处理过了。
        """
        return re.sub(r"<[^>]+>", "", text)

    @staticmethod
    def _remove_urls(text: str) -> str:
        """
        去除 URL 链接。

        正则 https?://\S+ 的含义：
        https?  匹配 "http" 或 "https"
        ://     匹配协议分隔符
        \S+     匹配一个或多个非空白字符（URL 中不会有空格）

        例如："请访问 https://example.com/page 了解更多"
        变成："请访问  了解更多"
        """
        return re.sub(r"https?://\S+", "", text)

    @staticmethod
    def _remove_control_chars(text: str) -> str:
        """
        去除不可见的控制字符。

        保留：\n（换行，ASCII 10）、\t（制表符，ASCII 9）
        去除：\x00-\x08（NULL 到退格）、\x0b\x0c（垂直/换页）、
              \x0e-\x1f（其他控制字符）、\x7f-\x9f（DEL + 扩展控制字符）

        这些字符在文本中不可见，但会干扰向量化计算。
        """
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)

    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """
        空白规范化。

        两步操作：
        1. 合并连续空格/制表符为单个空格
            "hello    world"  →  "hello world"
        2. 最多保留两个连续换行
            "段落1\n\n\n\n段落2"  →  "段落1\n\n段落2"

        这样既保留了段落结构（一个空行分隔），又避免过多空白浪费 token。
        """
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    @staticmethod
    def _remove_empty_lines(text: str) -> str:
        """
        去除完全空白的行。

        保留含有空格/tab 的行（它们可能是有意义的缩进）。
        只去除 strip() 后为空的行。
        """
        return "\n".join(line for line in text.split("\n") if line.strip())