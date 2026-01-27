# Prompt templates for medical AI paper analysis

# LLM filter prompt: determines if paper is related to medical AI
TOPIC_RELATED_PROMPT = """判断以下论文是否与医疗AI相关。

论文标题：{title}
论文摘要：{abstract}

只判断是否属于以下三类之一：
1. 医疗大模型（医疗领域的语言模型、预训练模型、微调模型等）
2. 医疗数据集（医疗基准测试、医疗训练数据集、医疗评测等）
3. 医疗智能体（医疗决策系统、医疗Agent、临床推理系统等）

请只返回 "yes" 或 "no"，不要其他内容。"""

# Extract keywords, Chinese summary, and translated abstract from paper
EXTRACT_PAPER_INSIGHTS = """请分析以下论文信息，返回JSON格式：

论文标题：{title}
论文摘要：{abstract}

请返回包含以下字段的JSON：
{{
    "keywords": "关键词1, 关键词2, 关键词3（3-5个，用逗号分隔）",
    "summary": "100字以内的中文总结",
    "abstract_cn": "将摘要翻译成中文，保留专业术语的英文并用括号标注"
}}"""
