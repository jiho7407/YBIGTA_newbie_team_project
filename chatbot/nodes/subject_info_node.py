"""
Subject Info 노드 (재훈 담당)

영화 "기생충"의 기본 정보를 제공하는 노드입니다.
(감독, 배우, 수상 내역, 줄거리 등)

구현 가이드:
- utils.state.ChatState를 import하여 사용
- state["messages"][-1]에서 사용자 질문 확인
- 반환값: {"subject_context": "영화 정보 문자열"}

접근 방식 (택 1):
- 하드코딩된 영화 정보 딕셔너리
- 외부 API (TMDb, OMDb 등) 호출
- 별도 DB 테이블 조회
"""

from utils.state import ChatState


def subject_info_node(state: ChatState) -> dict:
    # TODO: 재훈 구현
    # 1. 사용자 질문 분석
    # 2. 기생충 영화 정보에서 관련 내용 추출
    # 3. 문자열로 포맷팅하여 반환
    return {"subject_context": ""}
