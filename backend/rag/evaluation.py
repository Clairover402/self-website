"""
=============================================================================
RAG 评估模块 — RAGAS + LangSmith
=============================================================================

【RAG 评估为什么重要】
开发 RAG 系统时，你需要回答：
- 我的检索到底准不准？（Context Precision / Recall）
- 生成的答案是否忠实于检索到的文档？（Faithfulness）
- 答案和问题是否相关？（Answer Relevancy）

没有评估就是"盲飞"——你改了一个参数（如 chunk_size），
但不知道效果变好还是变差。

【类比 Java 中的单元测试】
RAGAS 评估 ≈ JUnit 集成测试：
- 预先准备测试数据（问题 + 预期答案）
- 跑一遍 RAG 管线
- 自动对比生成结果和预期结果
- 给出量化指标

【RAGAS 四大指标】

1. Faithfulness（忠实度）
   答案中的每句话是否都能在检索到的文档中找到依据？
   类比：SQL 查询结果中的每一行是否都来源于表数据（而非凭空捏造）

2. Answer Relevancy（答案相关性）
   答案是否紧扣问题？有没有跑题？
   类比：REST API 的响应是否只包含请求的字段

3. Context Precision（上下文精度）
   检索到的文档中，相关的排得有多靠前？
   类比：搜索引擎的 P@K 指标

4. Context Recall（上下文召回率）
   检索到的文档覆盖了预期答案的多少内容？
   类比：MySQL 索引的召回率

【LangSmith 是什么】
LangChain 官方的 LLM 应用可观测性平台，可以追踪：
- 每次 LLM 调用的 token 消耗和延迟
- 检索过程的时间分布
- Prompt 的版本和效果对比
类似 Java 中的 APM 工具（如 SkyWalking、Pinpoint），
但专为 LLM 应用设计。

使用前需配置环境变量：
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=你的key
    LANGCHAIN_PROJECT=项目名
"""

import json
from typing import List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# =========================================================================
# 数据模型
# =========================================================================

@dataclass
class EvalSample:
    """
    单个评估样本。

    对应测试数据集中的一行：
    {
        "question": "什么是 RAG？",
        "ground_truth": "RAG 是一种结合检索和生成的技术...",
    }

    运行评估后 answer 和 contexts 会被填充。
    """
    question: str            # 测试问题
    ground_truth: str        # 预期答案（人工标注的"标准答案"）
    answer: str = ""         # RAG 系统实际生成的答案（评估时填充）
    contexts: List[str] = None  # 检索到的文档片段（评估时填充）

    def __post_init__(self):
        """__post_init__ 在 __init__ 之后自动调用，确保 contexts 不为 None"""
        if self.contexts is None:
            self.contexts = []


@dataclass
class EvalResult:
    """
    评估结果 —— 所有样本的指标均值。

    每个指标范围 [0, 1]，1 表示最好。
    """
    faithfulness: float = 0.0        # 忠实度
    answer_relevancy: float = 0.0    # 答案相关性
    context_precision: float = 0.0   # 上下文精度
    context_recall: float = 0.0      # 上下文召回率
    sample_count: int = 0            # 评估样本数


# =========================================================================
# 测试数据加载
# =========================================================================

def load_test_data(path: str) -> List[EvalSample]:
    """
    从 JSON 文件加载评估数据集。

    JSON 格式示例：
    [
        {"question": "什么是 RAG？", "ground_truth": "RAG 是..."},
        {"question": "网站用了什么技术？", "ground_truth": "Vue 3 + FastAPI..."},
    ]

    每个对象被解包为 EvalSample 构造参数。
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvalSample(**item) for item in data]


# =========================================================================
# RAGAS 评估
# =========================================================================

def evaluate_with_ragas(samples: List[EvalSample]) -> EvalResult:
    """
    使用 RAGAS 框架计算评估指标。

    【RAGAS 工作原理】
    RAGAS 本身也使用 LLM 来做评估（LLM-as-Judge 模式）：
    - 比如评估 Faithfulness 时，RAGAS 会用 LLM 判断答案中的每个声明
      是否能在参考上下文中找到依据
    - 这意味着评估过程也会消耗 token（需要配置 LLM）

    类比：用另一个程序来测试你的程序（集成测试）

    【导入放在函数内部的原因】
    ragas 是可选依赖，不是所有环境都需要。
    放在函数内 import，只有真正调用时才加载，避免启动时报错。
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,          # 忠实度
            answer_relevancy,      # 答案相关性
            context_precision,     # 上下文精度
            context_recall,        # 上下文召回率
        )
        from ragas.dataset_schema import SingleTurnSample

        # 将我们的数据结构转为 RAGAS 期望的格式
        ragas_samples = []
        for s in samples:
            ragas_samples.append(SingleTurnSample(
                user_input=s.question,          # 用户问题
                response=s.answer,              # RAG 生成的答案
                reference=s.ground_truth,       # 人工标注的标准答案
                retrieved_contexts=s.contexts,   # 检索到的文档
            ))

        # 运行评估（这一步最耗时，每个样本都要调用 LLM 做判断）
        result = evaluate(
            dataset=ragas_samples,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall,
            ],
        )

        # 提取均值
        df = result.to_pandas()
        return EvalResult(
            faithfulness=float(df["faithfulness"].mean()),
            answer_relevancy=float(df["answer_relevancy"].mean()),
            context_precision=float(df["context_precision"].mean()),
            context_recall=float(df["context_recall"].mean()),
            sample_count=len(samples),
        )

    except ImportError:
        print("⚠️  ragas 未安装，跳过评估。运行 pip install ragas 安装。")
        return EvalResult(sample_count=len(samples))


# =========================================================================
# 完整评估流程
# =========================================================================

def generate_eval_report(
    test_data_path: str,
    kb_id: Optional[str] = None,
    output_path: Optional[str] = None,
) -> EvalResult:
    """
    完整评估流程：加载数据 → 运行查询 → 计算指标 → 输出报告。

    这是评估的"一键式"入口。
    """
    # 1. 加载测试数据
    samples = load_test_data(test_data_path)
    print(f"📊 加载 {len(samples)} 个评估样本")

    # 2. 对每个问题执行 RAG 查询
    # 延迟导入：避免评估脚本依赖整个服务
    from services.rag_service import RAGService
    service = RAGService()

    for i, sample in enumerate(samples):
        print(f"  [{i + 1}/{len(samples)}] 查询: {sample.question[:50]}...")
        result = service.query(sample.question, kb_id)
        sample.answer = result.answer
        sample.contexts = result.sources

    # 3. RAGAS 评估
    print("\n📐 计算 RAGAS 指标...")
    eval_result = evaluate_with_ragas(samples)

    # 4. 输出报告
    report = {
        "metrics": asdict(eval_result),
        "samples": [asdict(s) for s in samples],
    }

    if output_path:
        Path(output_path).write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"📝 报告已保存到 {output_path}")

    print(f"\n{'='*40}")
    print(f"  RAG 评估报告")
    print(f"{'='*40}")
    print(f"  样本数:           {eval_result.sample_count}")
    print(f"  Faithfulness:      {eval_result.faithfulness:.4f}")
    print(f"  Answer Relevancy:  {eval_result.answer_relevancy:.4f}")
    print(f"  Context Precision: {eval_result.context_precision:.4f}")
    print(f"  Context Recall:    {eval_result.context_recall:.4f}")
    print(f"{'='*40}")

    return eval_result


# =========================================================================
# CLI 入口
# =========================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RAG 评估工具")
    parser.add_argument("--test-data", required=True, help="测试数据 JSON 文件路径")
    parser.add_argument("--kb-id", default=None, help="知识库 ID（可选，不传则用默认库）")
    parser.add_argument("--output", default=None, help="评估报告 JSON 输出路径")
    args = parser.parse_args()

    generate_eval_report(args.test_data, args.kb_id, args.output)
