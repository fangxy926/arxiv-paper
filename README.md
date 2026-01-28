# arXiv 学术进展周报

自动生成医疗 AI 领域的 arXiv 论文周报，支持 GitHub Actions 自动部署到 GitHub Pages。

## 功能特性

- **自动搜索**: 每周一自动搜索上周的 arXiv 论文
- **LLM 智能筛选**: 使用大语言模型筛选相关论文并提取关键信息
- **主题分类**: 按配置的主题自动分类论文
- **历史存档**: 按年/月/日目录结构保存历史报告
- **静态网站**: 生成可浏览的历史报告索引页面

## 项目结构

```
.
├── .github/workflows/      # GitHub Actions 工作流
│   └── weekly-report.yml   # 每周自动生成报告
├── docs/                   # GitHub Pages 静态网站目录
│   ├── index.html          # 历史报告索引页
│   ├── .nojekyll           # 禁用 Jekyll 处理
│   └── YYYY/MM/DD/         # 按日期组织的报告目录
│       ├── index.html      # 当日报告
│       └── metadata.json   # 报告元数据
├── main.py                 # 主运行脚本
├── search_arxiv_medical.py # arXiv 搜索模块
├── extract_paper_insights.py # LLM 信息提取模块
├── categorize_papers.py    # 论文分类模块
├── generate_html_report.py # HTML 报告生成
├── generate_index.py       # 索引页面生成
├── llm.py                  # LLM 客户端封装
├── prompts.py              # LLM 提示词模板
├── .env.example            # 环境变量示例
└── CLAUDE.md               # 项目说明文档
```

## 本地开发

### 1. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install arxiv openai python-dotenv httpx
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填写你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM API 配置 (OpenAI 兼容格式)
OPENAI_API_BASE=https://your-api-endpoint.com/v1
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4o-mini

# arXiv 搜索配置
ARXIV_DAYS_BACK=7           # 搜索天数
ARXIV_MAX_RESULTS=50        # 每个搜索词最大结果数

# 主题配置 (逗号分隔)
TOPICS=医疗大模型,医疗数据集,医疗智能体

# 关键词过滤 (逗号分隔)
FILTER_KEYWORDS=medical,clinical,healthcare,...
```

### 3. 本地运行

```bash
# 运行完整流程
.venv/Scripts/python.exe main.py

# 或分步运行
.venv/Scripts/python.exe search_arxiv_medical.py
.venv/Scripts/python.exe extract_paper_insights.py
.venv/Scripts/python.exe categorize_papers.py
.venv/Scripts/python.exe generate_html_report.py
```

本地运行将生成 `medical_ai_report.html` 文件。

## GitHub Actions 部署

### 1. 设置仓库为 Public

GitHub Pages 免费托管要求仓库必须是 **Public**。在仓库的 Settings -> General -> Danger Zone 中：
- 点击 "Change visibility"
- 选择 "Make public"

### 2. 配置 Secrets 和 Variables

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中配置：

**⚠️ 重要：使用 Environment 配置**

由于 workflow 使用了 `environment: Default`，需要在 **Environment secrets** 中配置：

1. 点击 **Manage environment secrets**
2. 创建或选择 **Default** 环境
3. 在该环境下添加：

**Secrets (加密):**
- `OPENAI_API_KEY`: LLM API 密钥

**Variables (非加密):**
- `OPENAI_API_BASE`: LLM API 基础 URL (如: `https://api.deepseek.com/v1`)
- `OPENAI_MODEL`: 模型名称 (默认: `gpt-4o-mini`)
- `TOPICS`: 主题列表 (默认: `医疗大模型,医疗数据集,医疗智能体`)
- `FILTER_KEYWORDS`: 过滤关键词

### 3. 启用 GitHub Pages

在仓库的 **Settings → Pages** 中：
1. Source 选择 **GitHub Actions**
2. 点击 **Save**

**⚠️ 注意：必须先完成步骤 1（设为 Public），否则会出现 "Resource not accessible by integration" 错误。**

### 4. 自动运行

- **定时执行**: 每周一 00:00 UTC (北京时间 08:00) 自动运行
- **手动触发**: 在 Actions 页面点击 "Run workflow"

### 5. 访问网站

部署完成后，访问 `https://your-username.github.io/your-repo-name/`

## 常见问题排查

### Error: "Resource not accessible by integration"

**原因**: 仓库未设置为 Public，或 GitHub Pages 未启用。

**解决**:
1. 确保仓库是 **Public**（Settings → General → Danger Zone）
2. 确保已启用 GitHub Pages（Settings → Pages → Source: GitHub Actions）

### Error: "LLM client is required to generate search terms"

**原因**: `OPENAI_API_KEY` 未正确配置或 workflow 无法访问 Environment secrets。

**解决**:
1. 确认 `OPENAI_API_KEY` 配置在 **Environment secrets** 中（不是 Repository secrets）
2. 确认 environment 名称为 **Default**
3. 确认 workflow 中设置了 `environment: Default`

### 无法访问部署的网站

**原因**: GitHub Pages 部署可能需要几分钟时间。

**解决**:
1. 在 Actions 页面确认 deploy job 已完成
2. 等待 2-3 分钟后刷新
3. 检查 URL 格式是否正确：`https://username.github.io/repo-name/`

## 自定义配置

### 修改执行时间

编辑 `.github/workflows/weekly-report.yml`：

```yaml
on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一 00:00 UTC
```

Cron 表达式格式：
- `0 0 * * 1` = 每周一 00:00
- `0 8 * * 1` = 每周一 08:00 (UTC)

### 添加自定义域名

在 `docs/` 目录下创建 `CNAME` 文件：

```bash
echo "your-domain.com" > docs/CNAME
```

## 工作原理

### 数据流程

```
search_arxiv_medical.py
       ↓
relative_papers.json
       ↓
extract_paper_insights.py
       ↓
categorize_papers.py
       ↓
categorized_papers.json
       ↓
generate_html_report.py + generate_index.py
       ↓
docs/YYYY/MM/DD/index.html + docs/index.html
       ↓
GitHub Pages
```

### 日期计算

GitHub Actions 执行时：
1. 获取当前日期
2. 计算上周一日期 (today - 7 - weekday)
3. 创建目录 `docs/YYYY/MM/DD/`
4. 生成该周的报告

### 历史索引

`generate_index.py` 会：
1. 扫描 `docs/` 目录下的所有日期目录
2. 读取每个报告的 `metadata.json`
3. 生成美观的历史索引页面

## 许可证

MIT License
