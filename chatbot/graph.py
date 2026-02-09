"""
LangGraph 그래프 정의 (지호 담당)

그래프 흐름:
    classify → (라우팅) → rag_review / subject_info / chat / fallback
                              ↓              ↓
                            chat            chat → END
"""

from langgraph.graph import StateGraph, END
from utils.state import ChatState
from chatbot.nodes.classify_node import classify_node
from chatbot.nodes.chat_node import chat_node
from chatbot.nodes.rag_review_node import rag_review_node
from chatbot.nodes.subject_info_node import subject_info_node


def route_by_intent(state: ChatState) -> str:
    """classify_node의 결과(intent)에 따라 다음 노드를 결정"""
    intent = state.get("intent", "general")
    if intent == "review_analysis":
        return "rag_review"
    elif intent == "subject_info":
        return "subject_info"
    elif intent == "general":
        return "chat"
    else:  # out_of_scope
        return "chat"


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
