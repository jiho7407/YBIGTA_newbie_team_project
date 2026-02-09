import os
from langchain_community.vectorstores import FAISS
from langchain_upstage import UpstageEmbeddings
from dotenv import load_dotenv

load_dotenv()

_vectorstore = None

def _load_vectorstore():
    global _vectorstore
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, "db", "faiss_index")
    
    embeddings = UpstageEmbeddings(model="solar-embedding-1-large")
    
    if os.path.exists(db_path):
        _vectorstore = FAISS.load_local(
            db_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
    else:
        print("Vector DB를 찾을 수 없습니다.")
        _vectorstore = None
    return _vectorstore

def get_retriever(site_filter="all", k=3):
    """
    조건에 맞는 Retriever를 반환합니다.
    - site_filter: "all", "imdb", "metacritic" 등
    """
    if _vectorstore is None:
        _load_vectorstore()
        
    if _vectorstore is None:
        raise ValueError("Vectorstore 로드 실패")

    search_kwargs = {"k": k}
    
    if site_filter and site_filter.lower() != "all":
        search_kwargs["filter"] = {"source": site_filter.lower()}
        
    return _vectorstore.as_retriever(search_kwargs=search_kwargs)