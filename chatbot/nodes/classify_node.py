"""
의도 분류 노드 (지호 담당)
사용자 메시지를 분석하여 intent를 결정합니다.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from utils.state import ChatState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

CLASSIFY_PROMPT = """당신은 영화 "기생충(Parasite, 2019)" 리뷰 분석 챗봇의 의도 분류기입니다.
사용자 메시지를 읽고 아래 4가지 중 하나로 분류하세요.

- review_analysis: 기생충 리뷰 내용, 관객 반응, 평점, 키워드 등에 대한 질문
- subject_info: 기생충 영화 자체의 정보 (감독, 배우, 줄거리, 수상 내역 등)
- general: 일반적인 인사, 챗봇 사용법 질문
- out_of_scope: 기생충과 관련 없는 질문

반드시 위 4개 중 하나만 답하세요. 다른 말은 하지 마세요."""


def classify_node(state: ChatState) -> dict:
    last_message = state["messages"][-1]
    response = llm.invoke([
        SystemMessage(content=CLASSIFY_PROMPT),
        last_message,
    ])
    intent = response.content.strip().lower()

    valid_intents = {"review_analysis", "subject_info", "general", "out_of_scope"}
    if intent not in valid_intents:
        intent = "general"

    return {"intent": intent}
