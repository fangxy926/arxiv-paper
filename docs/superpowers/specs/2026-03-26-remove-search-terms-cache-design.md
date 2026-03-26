# 移除 search_terms_cache 缓存机制设计文档

## 概述

移除 `search_terms_cache.json` 文件缓存机制，改为每次运行都重新生成搜索词。

## 问题背景

当前 `search_arxiv_medical.py` 使用 `search_terms_cache.json` 来缓存 LLM 生成的搜索词。缓存键基于主题哈希匹配，但没有过期时间。这导致：
- 搜索词可能长期不更新，无法反映最新的研究热点
- 缓存逻辑增加了代码复杂度

## 设计目标

1. 简化代码，移除缓存相关逻辑
2. 确保每次运行都生成最新的搜索词
3. 保持现有功能不变

## 变更范围

### 文件变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `search_arxiv_medical.py` | 修改 | 移除缓存相关代码 |
| `search_terms_cache.json` | 删除 | 不再需要的缓存文件 |

### 具体变更

#### 1. 移除常量
```python
# 删除以下常量
SEARCH_TERMS_CACHE_FILE = "search_terms_cache.json"
```

#### 2. 移除函数
```python
# 删除以下函数
def load_search_terms_cache()
def save_search_terms_cache(topics, terms)
```

#### 3. 修改 generate_search_terms 函数

**当前逻辑：**
1. 检查缓存是否存在且主题匹配
2. 如果匹配，返回缓存的搜索词
3. 如果不匹配，调用 LLM 生成搜索词
4. 保存到缓存

**新逻辑：**
1. 直接调用 LLM 生成搜索词
2. 返回搜索词

#### 4. 删除缓存文件
如果 `search_terms_cache.json` 存在，将其删除。

## 代码变更详情

### search_arxiv_medical.py

移除以下内容：
- `SEARCH_TERMS_CACHE_FILE` 常量
- `load_search_terms_cache()` 函数
- `save_search_terms_cache()` 函数
- `generate_search_terms()` 中的缓存检查逻辑

修改后的 `generate_search_terms` 函数：
```python
def generate_search_terms(client, topics, max_retries=2):
    """使用 LLM 根据给定主题生成 arXiv 搜索词
    返回: list of search terms
    """
    if not client:
        raise ValueError("LLM client is required to generate search terms")

    prompt = GENERATE_SEARCH_TERMS_PROMPT.format(topics=topics)

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,
                max_tokens=2048
            )

            if not response.choices:
                raise ValueError("Empty response choices")

            content = response.choices[0].message.content.strip()
            content_clean = clean_markdown_code_blocks(content)
            result = json.loads(content_clean)
            terms = result.get('search_terms', [])

            if terms and len(terms) >= 1:
                print(f"[INFO] Generated {len(terms)} search terms for topics: {topics}")
                return terms

        except json.JSONDecodeError as e:
            print(f"[WARN] Failed to parse LLM response: {e}")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            print(f"[WARN] Failed to generate search terms: {e}")
            if attempt < max_retries - 1:
                continue

    raise ValueError("Failed to generate search terms from LLM")
```

## 优势

1. **搜索词新鲜度**：每次运行都基于当前研究热点生成搜索词
2. **代码简化**：移除约20行缓存相关代码
3. **减少依赖**：不再依赖文件系统缓存

## 潜在考虑

- **API 调用成本**：每次运行都会调用 LLM 生成搜索词（约1次API调用，成本可忽略）
- **运行时间**：增加约1-2秒的运行时间

## 验收标准

- [ ] `SEARCH_TERMS_CACHE_FILE` 常量已移除
- [ ] `load_search_terms_cache()` 函数已移除
- [ ] `save_search_terms_cache()` 函数已移除
- [ ] `generate_search_terms()` 不再检查或保存缓存
- [ ] `search_terms_cache.json` 文件已删除（如果存在）
- [ ] 代码可以正常运行并生成搜索词
