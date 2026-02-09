from utils.state import ChatState
from rag.retriever import get_retriever
from rag.prompt import get_rag_prompt
from rag.llm import get_llm
from langchain_core.messages import AIMessage

def format_docs_with_metadata(docs):
    """
    검색된 문서들을 LLM에 넣기 좋게 포맷팅합니다.
    출처(Source)를 함께 표기하여 LLM이 인용할 수 있게 합니다.
    """
    formatted_list = []
    for doc in docs:
        source = doc.metadata.get("source", "Unknown Site")
        content = doc.page_content
        formatted_list.append(f"[{source} 리뷰] {content}")
    return "\n\n".join(formatted_list)

def rag_review_node(state: ChatState):
    """
    RAG(검색 증강 생성)를 수행하는 노드입니다.
    1. State에서 질문과 필터 정보를 가져옵니다.
    2. 필터에 맞는 Retriever를 가져와 검색합니다.
    3. LLM을 통해 답변을 생성합니다.
    4. 결과 메시지와 검색된 컨텍스트를 State에 업데이트합니다.
    """
    print("\n--- RAG REVIEW NODE ---")
    
    question = state["messages"][-1].content
    site_filter = state.get("site_filter", "all")
    
    print(f"검색 필터 적용: {site_filter}")

    retriever = get_retriever(site_filter=site_filter)

    docs = retriever.invoke(question)

    context_text = format_docs_with_metadata(docs)

    prompt = get_rag_prompt()
    llm = get_llm()
    
    chain = prompt | llm
    
    response = chain.invoke({
        "context": context_text,
        "question": question
    })

    return {
        "messages": [response],
        "review_context": context_text
    }