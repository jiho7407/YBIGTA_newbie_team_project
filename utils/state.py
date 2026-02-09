"""
공유 State 정의 - 모든 LangGraph 노드가 이 State를 사용합니다.

팀원 모두 이 파일을 import해서 사용하세요:
    from utils.state import ChatState
"""

from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    """LangGraph 그래프 전체에서 공유되는 상태 객체"""

    # 대화 메시지 이력 (LangGraph가 자동으로 append 처리)
    messages: Annotated[List[BaseMessage], add_messages]

    # 라우팅 판단용 의도 분류 결과
    # "review_analysis" | "subject_info" | "general" | "out_of_scope"
    intent: str

    # RAG 검색으로 가져온 리뷰 데이터 (현종 담당)
    review_context: str

    # 영화 기본 정보 컨텍스트 (재훈 담당)
    subject_context: str

    # 리뷰 사이트 필터 ("all" | "imdb" | "metacritic" | "rottentomatoes")
    site_filter: str
