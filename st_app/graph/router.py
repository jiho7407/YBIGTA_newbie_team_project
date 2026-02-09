"""
LangGraph 그래프 & 라우팅 정의 (지호 담당)

그래프 흐름:
    classify → (라우팅) → rag_review / subject_info / chat
                              ↓              ↓
                            chat            chat → END
"""

from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from st_app.utils.state import ChatState
from st_app.graph.nodes.chat_node import chat_node
from st_app.graph.nodes.rag_review_node import rag_review_node
from st_app.graph.nodes.subject_info_node import subject_info_node

# --- 의도 분류 (classify) ---

_classify_llm = None


def _get_classify_llm():
    global _classify_llm
    if _classify_llm is None:
        _classify_llm = ChatUpstage(model="solar-mini", temperature=0)
    return _classify_llm


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
    """사용자 메시지를 분석하여 intent를 결정"""
    last_message = state["messages"][-1]
    response = _get_classify_llm().invoke([
        SystemMessage(content=CLASSIFY_PROMPT),
        HumanMessage(content=last_message.content),
    ])
    intent = response.content.strip().lower().replace(" ", "_")

    valid_intents = {"review_analysis", "subject_info", "general", "out_of_scope"}
    if intent not in valid_intents:
        intent = "general"

    return {"intent": intent}


# --- 조건부 라우팅 ---

def route_by_intent(state: ChatState) -> str:
    """classify_node의 결과(intent)에 따라 다음 노드를 결정"""
    intent = state.get("intent", "general")
    if intent == "review_analysis":
        return "rag_review"
    elif intent == "subject_info":
        return "subject_info"
    else:  # general, out_of_scope
        return "chat"


# --- 그래프 구성 ---

def build_graph() -> StateGraph:
    graph = StateGraph(ChatState)

    # 노드 등록
    graph.add_node("classify", classify_node)
    graph.add_node("rag_review", rag_review_node)
    graph.add_node("subject_info", subject_info_node)
    graph.add_node("chat", chat_node)

    # 엣지 연결
    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", route_by_intent, {
        "rag_review": "rag_review",
        "subject_info": "subject_info",
        "chat": "chat",
    })
    graph.add_edge("rag_review", "chat")
    graph.add_edge("subject_info", "chat")
    graph.add_edge("chat", END)

    return graph


# 컴파일된 그래프 (import해서 사용)
chatbot_graph = build_graph().compile()
