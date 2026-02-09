"""
Streamlit UI → LangGraph 실행 진입점

실행: streamlit run streamlit_app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

st.set_page_config(page_title="기생충 리뷰 챗봇", page_icon="🎬", layout="centered")
st.title("🎬 기생충(Parasite) 리뷰 분석 챗봇")

# --- API 키 체크 ---
if not os.getenv("UPSTAGE_API_KEY"):
    st.error("UPSTAGE_API_KEY가 설정되지 않았습니다. .env 파일 또는 Streamlit Secrets를 확인하세요.")
    st.stop()

from st_app.graph.router import chatbot_graph  # noqa: E402

# --- 사이드바 ---
with st.sidebar:
    st.header("설정")
    site_filter = st.selectbox(
        "리뷰 사이트 필터",
        ["all", "imdb", "metacritic", "rottentomatoes"],
        format_func=lambda x: "전체" if x == "all" else x.upper(),
    )
    st.markdown("---")
    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.session_state.langchain_messages = []
        st.rerun()

    st.markdown("---")
    st.caption("YBIGTA 2조 - 기생충 리뷰 분석")

# --- 대화 이력 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.langchain_messages = []

# --- 기존 메시지 렌더링 ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("review_context"):
            with st.expander("참고한 리뷰 데이터"):
                st.text(msg["review_context"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("기생충 리뷰에 대해 질문해보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.langchain_messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            try:
                result = chatbot_graph.invoke({
                    "messages": list(st.session_state.langchain_messages),
                    "intent": "",
                    "review_context": "",
                    "subject_context": "",
                    "site_filter": site_filter,
                })

                response = result["messages"][-1].content
                review_ctx = result.get("review_context", "")

                st.markdown(response)

                if review_ctx:
                    with st.expander("참고한 리뷰 데이터"):
                        st.text(review_ctx)

            except Exception as e:
                response = f"오류가 발생했습니다: {e}"
                review_ctx = ""
                st.error(response)

    st.session_state.langchain_messages.append(AIMessage(content=response))
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "review_context": review_ctx,
    })
