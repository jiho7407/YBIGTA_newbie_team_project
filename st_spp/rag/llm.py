import os
from langchain_upstage import ChatUpstage
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """
    Upstage Solar Mini 모델 인스턴스를 반환합니다.
    """
    llm = ChatUpstage(
        model="solar-mini",
        temperature=0,
    )
    return llm