"""
FAISS 인덱스 구축 (현종 작성 → 구조 통합)

리뷰 CSV 데이터를 Upstage 임베딩으로 벡터화하여 FAISS 인덱스를 생성합니다.

실행: python -m st_app.rag.embedder
"""

import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(PROJECT_ROOT, "database", "total_reviews.csv")
FAISS_DIR = os.path.join(PROJECT_ROOT, "st_app", "db", "faiss_index")


def create_vector_db():
    if not os.path.exists(CSV_PATH):
        print(f"데이터 파일이 없습니다: {CSV_PATH}")
        return

    print(f"Reading {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)

    # 속도 개선: 사이트별 상위 10개만 사용 (source_site 컬럼 기준)
    if "source_site" in df.columns:
        df = df.sort_index().groupby("source_site", as_index=False).head(10)
    else:
        df = df.head(10)

    documents = []
    for _, row in df.iterrows():
        text = str(row["content"])
        site = str(row.get("source_site", "unknown")).lower()

        metadata = {
            "source": site,
            "rating": row.get("rating", 0),
            "date": str(row.get("date", "")),
        }
        documents.append(Document(page_content=text, metadata=metadata))

    print(f"총 {len(documents)}개의 문서를 벡터화합니다...")

    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    vectorstore = FAISS.from_documents(documents, embeddings)

    os.makedirs(FAISS_DIR, exist_ok=True)
    vectorstore.save_local(FAISS_DIR)
    print(f"Vector DB 저장 완료: {FAISS_DIR}")


if __name__ == "__main__":
    create_vector_db()
