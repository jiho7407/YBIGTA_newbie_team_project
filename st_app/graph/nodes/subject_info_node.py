"""
Subject Info 노드 (재훈 담당)

영화 "기생충"의 기본 정보를 제공하는 노드입니다.
st_app/db/subject_information/subjects.json에서 정보를 로드합니다.

구현 가이드:
- st_app.utils.state.ChatState를 import하여 사용
- state["messages"][-1]에서 사용자 질문 확인
- st_app/db/subject_information/subjects.json에서 영화 정보 로드
- 반환값: {"subject_context": "영화 정보 문자열"}
"""

from st_app.utils.state import ChatState


def subject_info_node(state: ChatState) -> dict:
    # TODO: 재훈 구현
    # 1. subjects.json에서 기생충 정보 로드
    # 2. 사용자 질문에 맞는 정보 추출
    # 3. 문자열로 포맷팅하여 반환
    return {"subject_context": ""}
