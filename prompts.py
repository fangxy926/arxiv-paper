# Prompt templates for paper analysis

# LLM filter prompt: determines if paper is related to given topics and which topic(s) it belongs to
TOPIC_RELATED_PROMPT = """判断以下论文是否与给定的主题相关，并返回具体所属的主题。

论文标题：{title}
论文摘要：{abstract}

只判断是否属于以下给定的主题：{topics}

请按照以下JSON格式返回（不要用markdown包裹，仅输出JSON字符串）：
{{
    "related": true 或 false,
    "topics": ["主题1", "主题2"] 或 []
}}
"""

# Generate arXiv search terms based on given topics
GENERATE_SEARCH_TERMS_PROMPT = """根据以下研究主题，生成用于 arXiv 搜索的关键词组合。

研究主题：{topics}

请生成 5 个搜索词/词组，每个搜索词应该：
1. 精确匹配该领域的研究热点
2. 适合在 arXiv 上搜索学术论文
3. 包含主题相关的英文关键词
4. 不要使用过于宽泛的词

请按照以下JSON格式返回（不要用markdown包裹，仅输出JSON字符串）：
{{
    "search_terms": ["搜索词1", "搜索词2", "搜索词3", "搜索词4", "搜索词5"]
}}

示例：
{{"search_terms": ["medical \"large language model\"", "clinical \"reasoning model\"", "\"medical dataset\" benchmark", "\"healthcare AI\" agent", "medical \"vision-language\" model"]}}
"""

# Extract keywords, Chinese summary, and translated abstract from paper
EXTRACT_PAPER_INSIGHTS = """请分析以下论文信息，返回JSON格式：

论文标题：{title}
论文摘要：{abstract}

请返回包含以下字段的JSON, 不要用markdown的JSON符号包裹，仅输出JSON字符串
{{
    "keywords": "关键词1, 关键词2, 关键词3（3-5个中文关键词，用逗号分隔）",
    "summary": "100字以内的中文总结",
    "abstract_cn": "将摘要翻译成中文，保留专业术语的英文并用括号标注"
}}
"""
