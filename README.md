# AI 智能客服综合平台

基于 **LangChain + FastAPI + Vue.js** 构建的 AI 综合平台，集智能客服、Text2SQL、BI 报表、AI 生图于一体。

---

## 环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10 | 后端运行环境 |
| MySQL | 8.0+ | 业务数据存储 |
| Redis | 5.0+ | 对话记忆存储 |
| Node.js | 16+ | 前端项目运行 |

---

## 快速启动

### 第一步：后端配置和启动

#### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填入必要配置：

```bash
# 阿里云百炼 API Key（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# MySQL 数据库配置（按需修改）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=ai_customer

# Redis 配置（按需修改）
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 2. 安装后端依赖

```bash
cd ai_customer_service
pip install -r requirements.txt
```

#### 3. 初始化数据库

在 MySQL 中执行建表脚本：

```bash
mysql -u root -p < scripts/init_db.sql
```

#### 4. 启动后端服务

```bash
# 方式一：默认端口（从 .env 读取，默认 8089）
python -m app.main

# 方式二：指定端口
python -m app.main --port 8089

# 方式三：直接运行
python app/main.py
```

启动后访问 http://localhost:8089 查看服务状态。

### 第二步：前端启动

前端项目位于 `frontend/` 目录下，是一个独立的 Vite + Vue 3 项目。

#### 1. 安装前端依赖

```bash
cd ai_customer_service/frontend
npm install
```

#### 2. 启动前端开发服务器

```bash
npm run dev
```

启动后访问 http://localhost:5173/ 即可使用。

**注意**：前端通过 Vite proxy 代理将 `/ai` 和 `/question` 请求转发到后端（默认 http://localhost:8089），
因此前端不需要手动配置后端地址。如果后端端口更改，请同步修改 `frontend/vite.config.ts` 中的 `target` 配置。

---

## 端口说明

| 端口 | 说明 |
|------|------|
| 8089 | 后端 FastAPI 服务（默认） |
| 5173 | 前端 Vite 开发服务器 |

> **注意**：Windows 系统可能将某些端口（如 8090）加入排除范围，
> 导致普通用户无法绑定。默认端口改为 **8089**，如需修改可在 `.env` 中调整 `SERVER_PORT`。

---

## 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务健康检查，查看所有可用端点 |
| `/ai/chat` | GET | 智能客服对话（支持 session_id、RAG 检索、角色化） |
| `/ai/stream` | GET | 流式对话（SSE 模式，支持 RAG 检索） |
| `/ai/chat/agent` | GET | Agent 工具调用聊天（Tool Calling，支持约课操作） |
| `/ai/chat/role` | GET | 角色化聊天（使用 AIRole 结构化角色定义） |
| `/ai/text2sql` | GET | 自然语言转 SQL 查询 |
| `/ai/charts` | GET | BI 图表分析（Text2SQL + 大模型分析 + 图表数据） |
| `/ai/image` | GET | AI 文生图（宣传海报） |
| `/ai/history` | GET | 获取对话历史 |
| `/ai/history` | DELETE | 删除对话历史 |
| `/question/grade` | GET | AI 阅卷评分 |

---

## 功能模块

### 模块一：AI 智能客服（增强版）

基于 ChatTongyi + Redis 对话记忆 + ChromaDB RAG 检索，支持多轮对话。

```bash
# 对话（普通输出，支持 RAG 检索）
curl "http://localhost:8089/ai/chat?msg=你好&session_id=1"

# 流式对话（SSE，支持 RAG 检索）
curl -N "http://localhost:8089/ai/stream?msg=你好&session_id=1"

# Agent 工具调用聊天（支持约课等操作）
curl "http://localhost:8089/ai/chat/agent?msg=帮小明预约数学课&session_id=1"

# 角色化聊天（结构化 AIRole 角色定义）
curl "http://localhost:8089/ai/chat/role?msg=介绍一下你自己&role_name=明星介绍助手&expertise=明星介绍和娱乐资讯"
```

### 模块二：Text2SQL

将自然语言转换为 SQL 并执行查询。

```bash
curl "http://localhost:8089/ai/text2sql?msg=查询所有学生信息"
```

### 模块三：BI 报表

自然语言查询 → Text2SQL → 大模型分析 → 返回图表数据。

```bash
curl "http://localhost:8089/ai/charts?text=查询薪资前5的教师"
```

返回格式：
```json
{
  "title": "薪资前5的教师",
  "xAxis": ["张三", "李四", "王五"],
  "series": [18000, 15000, 12000],
  "labels": ["张三", "李四", "王五"],
  "analysis": "本次数据展示了..."
}
```

### 模块四：AI 生图

基于 qwen-image-plus 模型生成宣传海报。

```bash
curl "http://localhost:8089/ai/image?prompt=生成一张瑜伽馆海报" --output poster.png
```

### 模块五：AI 阅卷

根据标准答案自动评分。

```bash
curl "http://localhost:8089/question/grade?question_id=1&user_answer=你的答案"
```

---

## 查询用例（BI 报表）

```
1. 查询薪资前5的教师
2. 统计学生的绩点分布
3. 根据入职年份查询教师薪资走向
4. 查询男学生、女学生各所占比例
5. 查询男教师、女教师的薪资各所占比例
6. 查询预约课程的取消比率
7. 查询各个课程的预约占比
8. 查询各位教师的总课时
9. 统计前3课程的各个预约名额
10. 统计绩点超过前5的学生
```

---

## 向量数据库初始化

如果有知识库文档（PDF/TXT），放入 `data/db/` 目录后执行：

```bash
python scripts/init_vector_store.py
```

---

## 常见问题

### 端口被占用

```bash
# 查看端口占用
netstat -ano | findstr :8089

# 查看 Windows 端口排除范围
netsh int ipv4 show excludedportrange protocol=tcp

# 换个端口启动
python -m app.main --port 8088
```

### 依赖安装失败

建议使用虚拟环境：

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# 再安装依赖
pip install -r requirements.txt
```

### MySQL 连接失败

检查 MySQL 服务是否启动，以及 `.env` 中的数据库配置是否正确。

### Redis 连接失败

如果不需要对话记忆功能，可以暂时注释掉 `chat_router.py` 中相关代码。

### 前端页面无法访问

确保先执行 `npm install` 安装依赖，再执行 `npm run dev` 启动开发服务器。
如果遇到端口冲突，可以在 `frontend/vite.config.ts` 中修改 `server.port` 配置。