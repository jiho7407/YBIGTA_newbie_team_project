# 기생충 리뷰 분석 챗봇 - TODO

## 프로젝트 구조 (명세 기준)

```
streamlit_app.py                        # Streamlit UI 진입점 (지호)
st_app/
├── db/
│   ├── subject_information/
│   │   └── subjects.json               # 영화 기본 정보 (재훈)
│   └── faiss_index/
│       ├── index.faiss                  # FAISS 인덱스 (현종)
│       └── meta.json                   # 리뷰 메타정보 (현종)
├── rag/
│   ├── embedder.py                     # FAISS 구축 (현종)
│   ├── retriever.py                    # RAG 검색 (현종)
│   ├── prompt.py                       # RAG 프롬프트 (현종)
│   └── llm.py                          # LLM 호출 (현종)
├── graph/
│   ├── nodes/
│   │   ├── chat_node.py                # 기본 대화 노드 (지호)
│   │   ├── subject_info_node.py        # 영화 정보 노드 (재훈)
│   │   └── rag_review_node.py          # RAG 리뷰 노드 (현종)
│   └── router.py                       # 조건부 라우팅 + 그래프 (지호)
└── utils/
    └── state.py                        # 공유 State 정의 (공통)
```

## 공유 인터페이스

- **State**: `st_app.utils.state.ChatState`를 모든 노드에서 사용
- **각 노드 함수 시그니처**: `def node_name(state: ChatState) -> dict`
- **반환값**: State에 업데이트할 필드만 dict로 반환

---

## 지호 (Chat Node / LangGraph 라우팅 / Streamlit UI)

- [x] `st_app/utils/state.py` - ChatState 정의
- [x] `st_app/graph/nodes/chat_node.py` - 채팅 노드
- [x] `st_app/graph/router.py` - 의도 분류 + 라우팅 + 그래프 구성
- [x] `streamlit_app.py` - Streamlit UI (멀티턴, 에러 핸들링)
- [x] 팀원용 스켈레톤 제공
- [ ] 현종/재훈 노드 통합 후 엔드투엔드 테스트
- [ ] Streamlit Cloud 배포
- [ ] Streamlit Cloud Secrets 설정 (UPSTAGE_API_KEY, MONGO_URL)
- [ ] README에 배포 URL + 작동 화면 첨부

---

## 현종 (RAG Review Node)

- [ ] `st_app/rag/embedder.py` - 리뷰 임베딩 & FAISS 인덱스 구축
- [ ] `st_app/db/faiss_index/index.faiss` + `meta.json` 생성
- [ ] `st_app/rag/retriever.py` - FAISS 검색 로직
- [ ] `st_app/rag/prompt.py` - RAG 프롬프트
- [ ] `st_app/rag/llm.py` - LLM 호출
- [ ] `st_app/graph/nodes/rag_review_node.py` - 노드 구현
  - `state["site_filter"]` 적용
  - 반환: `{"review_context": "검색된 리뷰"}`

---

## 재훈 (Subject Info Node)

- [ ] `st_app/db/subject_information/subjects.json` - 기생충 정보 작성
- [ ] `st_app/graph/nodes/subject_info_node.py` - 노드 구현
  - 반환: `{"subject_context": "영화 정보"}`

---

## 공통

- [x] `.env`에 `UPSTAGE_API_KEY` 추가
- [ ] 각자 브랜치에서 작업 후 PR → main 머지
- [ ] 통합 테스트 (전체 그래프 동작 확인)
- [ ] 명세서 CSV 작성 & README 업데이트
