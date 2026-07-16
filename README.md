# AI 智能客服综合平台

基于 **LangChain + FastAPI** 构建的 AI 综合平台，集智能客服、Text2SQL、BI 报表、AI 生图于一体。

---

## 环境要求

| 组件 | 版本 |
|------|------|
| Python | 3.10 |
| MySQL | 8.0+ |
| Redis | 5.0+ |
| Node.js | 16+（前端项目需要） |

---

## 快速启动

### 1. 配置环境变量

复制 `.env.example` 为 `.env`，填入必要配置：

```bash
# 阿里云百炼 API Key（必填）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx

# MySQL 数据库配置（按需修改）
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=db2

# Redis 配置（按需修改）
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. 安装依赖

```bash
cd ai_customer_service
pip install -r requirements.txt
```

### 3. 初始化数据库

在 MySQL 中执行建表脚本：

```bash
mysql -u root -p < scripts/init_db.sql
```

### 4. 启动服务

```bash
# 方式一：默认端口（从 .env 读取，默认 8089）
python -m app.main

# 方式二：指定端口
python -m app.main --port 8089

# 方式三：直接运行
python app/main.py
```

启动后访问 http://localhost:8089 查看服务状态。

---

## 端口说明

> **注意**：Windows 系统可能将某些端口（如 8090）加入排除范围，
> 导致普通用户无法绑定。默认端口改为 **8089**，如需修改可在 `.env` 中调整 `SERVER_PORT`。

---

## 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 服务健康检查，查看所有可用端点 |
| `/ai/chat` | GET | 智能客服对话（支持 session_id 区分会话） |
| `/ai/stream` | GET | 流式对话（SSE 模式） |
| `/ai/text2sql` | GET | 自然语言转 SQL 查询 |
| `/ai/charts` | GET | BI 图表分析（Text2SQL + 大模型分析 + 图表数据） |
| `/ai/image` | GET | AI 文生图（宣传海报） |
| `/ai/history` | GET | 获取对话历史 |
| `/ai/history` | DELETE | 删除对话历史 |
| `/question/grade` | GET | AI 阅卷评分 |

---

## 功能模块

### 模块一：AI 智能客服

基于 ChatTongyi + Redis 对话记忆，支持多轮对话。

```bash
# 对话（普通输出）
curl "http://localhost:8089/ai/chat?msg=你好&session_id=1"

# 流式对话（SSE）
curl -N "http://localhost:8089/ai/stream?msg=你好&session_id=1"
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