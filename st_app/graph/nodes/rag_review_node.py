"""
RAG Review 노드 (현종 담당)

FAISS 인덱스 기반으로 기생충 리뷰를 검색하여 review_context에 저장합니다.

구현 가이드:
- st_app.utils.state.ChatState를 import하여 사용
- state["messages"][-1]에서 사용자 질문 확인
- state["site_filter"]로 사이트 필터링 ("all" | "imdb" | "metacritic" | "rottentomatoes")
- st_app/rag/ 모듈의 retriever, llm, prompt를 활용
- 반환값: {"review_context": "검색된 리뷰 내용 문자열"}

FAISS 인덱스 위치: st_app/db/faiss_index/
RAG 모듈 위치: st_app/rag/
"""

from st_app.utils.state import ChatState


def rag_review_node(state: ChatState) -> dict:
    # TODO: 현종 구현
    # 1. 사용자 질문에서 검색 쿼리 생성
    # 2. st_app/rag/retriever.py로 FAISS 검색
    # 3. site_filter 적용하여 필터링
    # 4. 검색 결과를 문자열로 포맷팅하여 반환
    return {"review_context": ""}
