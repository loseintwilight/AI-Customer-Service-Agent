"""向量存储检索服务 — 集成 ChromaDB 实现 RAG 检索"""

from pathlib import Path

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from app.config import settings


class VectorStoreService:
    """向量存储检索服务，对应 Java 文档中的 QuestionAnswerAdvisor + VectorStore"""

    _instance: Chroma | None = None

    @classmethod
    def _get_vector_store(cls) -> Chroma | None:
        """懒加载 Chroma 向量存储"""
        if cls._instance is not None:
            return cls._instance

        persist_dir = (
            Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
        )
        if not persist_dir.exists():
            return None

        try:
            embeddings = DashScopeEmbeddings(
                model="text-embedding-v1",
                dashscope_api_key=settings.DASHSCOPE_API_KEY,
            )
            cls._instance = Chroma(
                persist_directory=str(persist_dir),
                embedding_function=embeddings,
            )
            return cls._instance
        except Exception:
            return None

    @classmethod
    def retrieve(cls, query: str, top_k: int = 2, threshold: float = 0.5) -> list[str]:
        """
        从向量库检索与查询最相似的文档片段

        Args:
            query: 查询文本
            top_k: 返回的最大文档数
            threshold: 相似度阈值（Chroma 默认使用余弦距离，此处为保留参数）

        Returns:
            检索到的文档内容列表
        """
        vector_store = cls._get_vector_store()
        if vector_store is None:
            return []

        try:
            retriever = vector_store.as_retriever(
                search_kwargs={"k": top_k}
            )
            docs = retriever.invoke(query)
            return [doc.page_content for doc in docs]
        except Exception:
            return []

    @classmethod
    def retrieve_with_scores(
        cls, query: str, top_k: int = 2
    ) -> list[tuple[str, float]]:
        """
        检索并返回相似度分数

        Args:
            query: 查询文本
            top_k: 返回的最大文档数

        Returns:
            [(文档内容, 相似度分数), ...]
        """
        vector_store = cls._get_vector_store()
        if vector_store is None:
            return []

        try:
            results = vector_store.similarity_search_with_score(query, k=top_k)
            return [(doc.page_content, score) for doc, score in results]
        except Exception:
            return []