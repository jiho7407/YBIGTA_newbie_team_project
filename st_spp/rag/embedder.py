import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

def create_vector_db():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    file_path = os.path.join(project_root, "database", "total_reviews.csv")
    db_path = os.path.join(project_root, "db", "faiss_index")

    if not os.path.exists(file_path):
        print(f"데이터 파일이 없습니다: {file_path}")
        return

    print(f"Reading {file_path}...")
    df = pd.read_csv(file_path)
    
    documents = []
    for _, row in df.iterrows():
        text = str(row['content'])
        site = str(row.get('source_site', 'unknown')).lower() 
        
        metadata = {
            "source": site,
            "rating": row.get('rating', 0),
            "date": row.get('date', '')
        }
        documents.append(Document(page_content=text, metadata=metadata))

    print(f"총 {len(documents)}개의 문서를 벡터화합니다...")

    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    vectorstore.save_local(db_path)
    print(f"Vector DB 저장 완료: {db_path}")

if __name__ == "__main__":
    create_vector_db()