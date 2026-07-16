"""
向量数据库初始化脚本

将知识库文档（PDF/TXT）读取、分割后写入 Chroma 向量数据库。
该脚本只需在首次部署或更新知识库时运行一次。

用法：
    cd ai_customer_service
    python scripts/init_vector_store.py
"""

import os
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

from app.config import settings


def init_vector_store():
    """初始化向量数据库"""
    print("=" * 50)
    print("向量数据库初始化开始")
    print("=" * 50)

    # 初始化嵌入模型
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v1",
        dashscope_api_key=settings.DASHSCOPE_API_KEY,
    )
    print("[✓] 嵌入模型已加载")

    # 文档存储目录
    data_dir = Path(__file__).resolve().parent.parent / "data" / "db"
    persist_dir = Path(__file__).resolve().parent.parent / "data" / "chroma_db"

    # 创建持久化目录
    persist_dir.mkdir(parents=True, exist_ok=True)

    all_documents = []

    # 1. 读取 PDF 文件
    pdf_files = list(data_dir.glob("*.pdf"))
    for pdf_path in pdf_files:
        print(f"[*] 正在读取 PDF: {pdf_path.name}")
        try:
            loader = PyPDFLoader(str(pdf_path))
            documents = loader.load()
            print(f"    → 读取到 {len(documents)} 页")
            all_documents.extend(documents)
        except Exception as e:
            print(f"    [✗] 读取失败: {e}")

    # 2. 读取 TXT 文件
    txt_files = list(data_dir.glob("*.txt"))
    for txt_path in txt_files:
        print(f"[*] 正在读取 TXT: {txt_path.name}")
        try:
            loader = TextLoader(str(txt_path), encoding="utf-8")
            documents = loader.load()
            print(f"    → 读取到 {len(documents)} 个文档")
            all_documents.extend(documents)
        except Exception as e:
            print(f"    [✗] 读取失败: {e}")

    if not all_documents:
        print("[!] 未找到任何文档，请将 PDF 或 TXT 文件放入 data/db/ 目录")
        return

    print(f"\n[*] 共读取到 {len(all_documents)} 个原始文档")

    # 3. 文本分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", "，", ",", " ", ""],
        length_function=len,
    )

    split_docs = text_splitter.split_documents(all_documents)
    print(f"[*] 文本分割完成，共 {len(split_docs)} 个文档片段")

    # 4. 写入向量数据库
    print("[*] 正在写入 Chroma 向量数据库...")
    vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=str(persist_dir),
    )
    vector_store.persist()
    print(f"[✓] 向量数据库已写入: {persist_dir}")
    print(f"    → 共 {len(split_docs)} 个向量")

    # 5. 验证
    print("\n[*] 验证向量数据库...")
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    test_query = "测试"
    results = retriever.invoke(test_query)
    print(f"    → 检索测试完成，可检索到 {len(results)} 条结果")

    print("\n" + "=" * 50)
    print("向量数据库初始化完成")
    print("=" * 50)


if __name__ == "__main__":
    init_vector_store()