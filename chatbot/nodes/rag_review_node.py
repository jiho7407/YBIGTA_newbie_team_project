"""
RAG Review 노드 (현종 담당)

MongoDB에서 기생충 리뷰 데이터를 검색하여 review_context에 저장합니다.

구현 가이드:
- utils.state.ChatState를 import하여 사용
- state["messages"][-1]에서 사용자 질문 확인
- state["site_filter"]로 사이트 필터링 ("all" | "imdb" | "metacritic" | "rottentomatoes")
- 반환값: {"review_context": "검색된 리뷰 내용 문자열"}

MongoDB 컬렉션:
- review_db.reviews_imdb
- review_db.reviews_metacritic
- review_db.reviews_rottentomatoes
- review_db.preprocessed_reviews_imdb (전처리 완료)
- review_db.preprocessed_reviews_metacritic (전처리 완료)
- review_db.preprocessed_reviews_rottentomatoes (전처리 완료)

CSV 컬럼: rating, date, content, Extreme_score, review_vector (전처리 후)
"""

from utils.state import ChatState


def rag_review_node(state: ChatState) -> dict:
    # TODO: 현종 구현
    # 1. 사용자 질문에서 키워드 추출
    # 2. MongoDB에서 관련 리뷰 검색 (site_filter 적용)
    # 3. 검색 결과를 문자열로 포맷팅하여 반환
    return {"review_context": ""}
