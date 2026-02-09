"""
Streamlit UI → LangGraph 실행 진입점

실행: streamlit run streamlit_app.py
"""

import os
import sys
import streamlit as st
from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

# .env 파일에서 환경 변수를 로드합니다 (로컬 개발용).
load_dotenv()

# Streamlit Cloud에서 패키지 경로가 누락되는 경우를 대비해 프로젝트 루트를 추가합니다.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

st.set_page_config(page_title="기생충 리뷰 챗봇", page_icon="🎬", layout="centered")
st.title("🎬 기생충(Parasite) 리뷰 분석 챗봇")

# --- API 키 체크 (Streamlit Cloud & Local) ---
api_key_found = False
try:
    # Streamlit Cloud의 secrets에 키가 있는지 확인
    if st.secrets.get("UPSTAGE_API_KEY"):
        api_key_found = True
except StreamlitSecretNotFoundError:
    # 로컬 환경에서 secrets.toml 파일이 없으면 이 오류가 발생하므로 무시합니다.
    pass

# secrets에 키가 없으면, 환경 변수(.env 파일)에서 확인
if not api_key_found:
    if os.getenv("UPSTAGE_API_KEY"):
        api_key_found = True

if not api_key_found:
    st.error("UPSTAGE_API_KEY가 설정되지 않았습니다. 로컬에서는 .env 파일에, Streamlit Cloud에서는 Secrets에 API 키를 등록해주세요.")
    st.stop()

# --- LangGraph 로컬 환경 패치 ---
# 일부 LangGraph 버전에서 empty_checkpoint의 versions_seen이 dict로 초기화되어
# '__start__' KeyError가 발생합니다. defaultdict로 보정합니다.
import langgraph.pregel as _pregel  # noqa: E402
import langgraph.checkpoint.base as _checkpoint_base  # noqa: E402

_orig_empty_checkpoint = _checkpoint_base.empty_checkpoint


def _patched_empty_checkpoint():
    cp = _orig_empty_checkpoint()
    cp["versions_seen"] = defaultdict(dict, cp.get("versions_seen", {}))
    return cp


_checkpoint_base.empty_checkpoint = _patched_empty_checkpoint
_pregel.empty_checkpoint = _patched_empty_checkpoint

# API 키가 확인된 후에 LangGraph 관련 모듈을 import 합니다.
# 이는 API 키가 없을 때 불필요한 초기화를 방지합니다.
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
                # chatbot_graph는 API 키를 자동으로 환경변수에서 읽어 사용합니다.
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
                import traceback
                traceback.print_exc()
                response = f"오류가 발생했습니다: {e}"
                review_ctx = ""
                st.error(response)

    st.session_state.langchain_messages.append(AIMessage(content=response))
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "review_context": review_ctx,
    })
