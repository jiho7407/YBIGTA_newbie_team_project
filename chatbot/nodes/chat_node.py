"""
채팅 노드 (지호 담당)
분류된 intent와 context를 바탕으로 최종 응답을 생성합니다.
"""

from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage
from utils.state import ChatState

llm = ChatUpstage(model="solar-mini", temperature=0.7)

SYSTEM_PROMPT = """당신은 영화 "기생충(Parasite, 2019)"에 대한 리뷰 분석 도우미입니다.
사용자의 질문에 친절하고 정확하게 답변하세요.

아래는 참고할 수 있는 컨텍스트입니다:

[리뷰 데이터]
{review_context}

[영화 정보]
{subject_context}

컨텍스트가 비어있으면 일반적인 지식으로 답변하되,
리뷰 데이터에 대한 질문이라면 "현재 검색된 리뷰 데이터가 없습니다"라고 안내하세요."""


def chat_node(state: ChatState) -> dict:
    review_ctx = state.get("review_context", "")
    subject_ctx = state.get("subject_context", "")

    system = SYSTEM_PROMPT.format(
        review_context=review_ctx if review_ctx else "(없음)",
        subject_context=subject_ctx if subject_ctx else "(없음)",
    )

    messages = [SystemMessage(content=system)] + list(state["messages"])
    response = llm.invoke(messages)

    return {"messages": [response]}
