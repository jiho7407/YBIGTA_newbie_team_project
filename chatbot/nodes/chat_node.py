"""
채팅 노드 (지호 담당)
분류된 intent와 context를 바탕으로 최종 응답을 생성합니다.
"""

from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage
from utils.state import ChatState

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatUpstage(model="solar-mini", temperature=0.7)
    return _llm

SYSTEM_PROMPT = """당신은 영화 "기생충(Parasite, 2019)"에 대한 리뷰 분석 도우미입니다.
한국어로 친절하게 답변하세요.

## 규칙
- 아래 [리뷰 데이터]나 [영화 정보]가 제공되면 반드시 해당 데이터를 근거로 답변하세요.
- 리뷰 데이터가 "(없음)"인데 리뷰 관련 질문이면: "현재 검색된 리뷰 데이터가 없습니다. 다시 질문해 주세요."
- 기생충과 무관한 질문이면: 정중히 범위를 안내하세요.
- 이전 대화 맥락을 고려하여 자연스럽게 이어서 답변하세요.

[리뷰 데이터]
{review_context}

[영화 정보]
{subject_context}"""


def chat_node(state: ChatState) -> dict:
    review_ctx = state.get("review_context", "")
    subject_ctx = state.get("subject_context", "")

    system = SYSTEM_PROMPT.format(
        review_context=review_ctx if review_ctx else "(없음)",
        subject_context=subject_ctx if subject_ctx else "(없음)",
    )

    messages = [SystemMessage(content=system)] + list(state["messages"])
    response = _get_llm().invoke(messages)

    return {"messages": [response]}
