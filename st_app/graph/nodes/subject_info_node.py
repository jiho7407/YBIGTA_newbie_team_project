"""
Subject Info 노드 (재훈 작성 → 구조 통합)

영화 "기생충"의 기본 정보를 subjects.json에서 로드하여 subject_context에 저장합니다.
이후 chat_node가 이 context를 바탕으로 최종 응답을 생성합니다.
"""

import json
import os
from st_app.utils.state import ChatState

_SUBJECT_DATA = None

SUBJECTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "db", "subject_information", "subjects.json",
)


def _load_subject_data() -> dict:
    global _SUBJECT_DATA
    if _SUBJECT_DATA is None:
        with open(SUBJECTS_PATH, "r", encoding="utf-8") as f:
            _SUBJECT_DATA = json.load(f)
    return _SUBJECT_DATA


def subject_info_node(state: ChatState) -> dict:
    """
    subjects.json에서 영화 정보를 로드하여 subject_context에 저장합니다.
    chat_node가 이 정보를 바탕으로 사용자 질문에 답변합니다.
    """
    movie_data = _load_subject_data()
    subject_context_str = json.dumps(movie_data, ensure_ascii=False, indent=2)

    return {"subject_context": subject_context_str}
