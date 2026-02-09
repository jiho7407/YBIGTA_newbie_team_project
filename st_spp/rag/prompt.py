from langchain_core.prompts import ChatPromptTemplate

def get_rag_prompt():
    template = """
    당신은 영화 리뷰 분석 AI 에이전트입니다.
    사용자의 질문에 대해 아래 제공된 [Review Context]만을 바탕으로 답변해야 합니다.
    
    - 특정 사이트(IMDb, Metacritic 등)에 대한 언급이 있다면 출처를 명시해주세요.
    - 리뷰 데이터에 없는 내용은 "제공된 리뷰 데이터에서는 관련 내용을 찾을 수 없습니다"라고 답하세요.
    - 한국어로 자연스럽게 답변하세요.

    [Review Context]
    {context}

    [User Question]
    {question}
    """
    return ChatPromptTemplate.from_template(template)