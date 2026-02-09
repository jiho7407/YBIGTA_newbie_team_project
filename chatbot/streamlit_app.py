"""
Streamlit 채팅 UI (지호 담당)

실행: streamlit run chatbot/streamlit_app.py
"""

import streamlit as st
from langchain_core.messages import HumanMessage
from chatbot.graph import chatbot_graph

st.set_page_config(page_title="기생충 리뷰 챗봇", page_icon="🎬", layout="centered")
st.title("🎬 기생충(Parasite) 리뷰 분석 챗봇")

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
        st.rerun()

    st.markdown("---")
    st.caption("YBIGTA 2조 - 기생충 리뷰 분석")

# --- 대화 이력 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 사용자 입력 ---
if prompt := st.chat_input("기생충 리뷰에 대해 질문해보세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            result = chatbot_graph.invoke({
                "messages": [HumanMessage(content=prompt)],
                "intent": "",
                "review_context": "",
                "subject_context": "",
                "site_filter": site_filter,
            })
            response = result["messages"][-1].content
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
