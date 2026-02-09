"""
의도 분류 노드 (지호 담당)
사용자 메시지를 분석하여 intent를 결정합니다.
"""

from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage, HumanMessage
from utils.state import ChatState

_llm = None

def _get_llm():
    global _llm
    if _llm is None:
        _llm = ChatUpstage(model="solar-mini", temperature=0)
    return _llm

CLASSIFY_PROMPT = """You are an intent classifier for a movie review chatbot about "Parasite (기생충, 2019)".
Classify the user's LAST message into exactly one of these categories:

- review_analysis : Questions about audience reviews, ratings, sentiments, keywords, review trends, comparisons across review sites (IMDb, Metacritic, RottenTomatoes)
- subject_info : Questions about the movie itself — director, cast, plot, awards, genre, runtime, box office
- general : Greetings, thank-you, chatbot usage questions, or follow-up acknowledgements like "ok", "thanks", "got it"
- out_of_scope : Anything unrelated to the movie Parasite

Rules:
1. Output ONLY one of the four labels above, nothing else.
2. If the message is ambiguous but mentions reviews/ratings/audience, choose review_analysis.
3. If the message is ambiguous but mentions the movie's content/people, choose subject_info.
4. Short affirmations ("네", "ㅇㅇ", "ok", "good") → general.
5. Messages in any language should be classified the same way."""


def classify_node(state: ChatState) -> dict:
    last_message = state["messages"][-1]
    response = _get_llm().invoke([
        SystemMessage(content=CLASSIFY_PROMPT),
        HumanMessage(content=last_message.content),
    ])
    intent = response.content.strip().lower().replace(" ", "_")

    valid_intents = {"review_analysis", "subject_info", "general", "out_of_scope"}
    if intent not in valid_intents:
        intent = "general"

    return {"intent": intent}
