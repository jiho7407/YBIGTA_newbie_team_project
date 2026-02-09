"""
LLM 호출 (현종 작성 → 구조 통합)
"""

from langchain_upstage import ChatUpstage


def get_llm():
    """Upstage Solar Mini 모델 인스턴스를 반환합니다."""
    return ChatUpstage(model="solar-mini", temperature=0)
