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
        try:
            _vectorstore = FAISS.load_local(
                FAISS_DIR,
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            raise ValueError(
                "FAISS 인덱스 로드 실패. 패키지 버전이 달라 인덱스가 호환되지 않을 수 있습니다. "
                "동일한 환경에서 `python -m st_app.rag.embedder`로 재생성하세요."
            ) from e
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
