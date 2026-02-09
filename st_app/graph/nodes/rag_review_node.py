"""
RAG Review 노드 (현종 작성 → 구조 통합)

FAISS 인덱스에서 관련 리뷰를 검색하여 review_context에 저장합니다.
이후 chat_node가 이 context를 바탕으로 최종 응답을 생성합니다.
"""

from st_app.utils.state import ChatState
from st_app.rag.retriever import get_retriever


def _format_docs_with_metadata(docs):
    """검색된 문서들을 출처와 함께 포맷팅합니다."""
    formatted_list = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        rating = doc.metadata.get("rating", "N/A")
        content = doc.page_content
        formatted_list.append(f"[{source} | 평점: {rating}] {content}")
    return "\n\n".join(formatted_list)


def rag_review_node(state: ChatState) -> dict:
    """
    1. State에서 질문과 필터 정보를 가져옵니다.
    2. FAISS retriever로 유사 리뷰를 검색합니다.
    3. review_context에 저장하여 chat_node로 전달합니다.
    """
    question = state["messages"][-1].content
    site_filter = state.get("site_filter", "all")

    try:
        retriever = get_retriever(site_filter=site_filter)
        docs = retriever.invoke(question)
        context_text = _format_docs_with_metadata(docs)
    except Exception as e:
        context_text = f"리뷰 검색 중 오류 발생: {e}"

    return {"review_context": context_text}
