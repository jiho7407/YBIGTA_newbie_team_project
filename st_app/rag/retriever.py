"""
RAG 검색 로직 (현종 작성 → 구조 통합)

FAISS 인덱스에서 쿼리와 유사한 리뷰를 검색합니다.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings
from dotenv import load_dotenv

load_dotenv()

_vectorstore = None

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAISS_DIR = os.path.join(PROJECT_ROOT, "st_app", "db", "faiss_index")


def _load_vectorstore():
    global _vectorstore
    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")

    if os.path.exists(FAISS_DIR):
        _vectorstore = FAISS.load_local(
            FAISS_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        print(f"Vector DB를 찾을 수 없습니다: {FAISS_DIR}")
        _vectorstore = None
    return _vectorstore


def get_retriever(site_filter="all", k=3):
    """
    조건에 맞는 Retriever를 반환합니다.
    - site_filter: "all", "imdb", "metacritic", "rottentomatoes"
    """
    global _vectorstore
    if _vectorstore is None:
        _load_vectorstore()

    if _vectorstore is None:
        raise ValueError("Vectorstore 로드 실패. embedder.py를 먼저 실행하세요.")

    search_kwargs = {"k": k}

    if site_filter and site_filter.lower() != "all":
        search_kwargs["filter"] = {"source": site_filter.lower()}

    return _vectorstore.as_retriever(search_kwargs=search_kwargs)
