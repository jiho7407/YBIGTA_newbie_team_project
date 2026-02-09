# 기생충 리뷰 분석 챗봇 - TODO

## 프로젝트 구조

```
chatbot/
├── graph.py                    # LangGraph 그래프 조합 (지호)
├── streamlit_app.py            # Streamlit 채팅 UI (지호)
└── nodes/
    ├── classify_node.py        # 의도 분류 노드 (지호)
    ├── chat_node.py            # 최종 응답 생성 노드 (지호)
    ├── rag_review_node.py      # RAG 리뷰 검색 노드 (현종)
    └── subject_info_node.py    # 영화 정보 노드 (재훈)
utils/
└── state.py                    # 공유 State 정의 (공통)
```

## 공유 인터페이스

- **State**: `utils/state.py`의 `ChatState`를 모든 노드에서 사용
- **각 노드 함수 시그니처**: `def node_name(state: ChatState) -> dict`
- **반환값**: State에 업데이트할 필드만 dict로 반환

---

## 지호 (Chat Node / LangGraph 라우팅 / Streamlit UI)

### Phase 1: 기반 구조 (완료)
- [x] `utils/state.py` - ChatState 정의
- [x] `chatbot/nodes/classify_node.py` - 의도 분류 노드 초안
- [x] `chatbot/nodes/chat_node.py` - 채팅 노드 초안
- [x] `chatbot/graph.py` - LangGraph 그래프 구성 & 라우팅
- [x] `chatbot/streamlit_app.py` - Streamlit UI 초안
- [x] 팀원용 노드 스켈레톤 제공 (rag_review_node, subject_info_node)

### Phase 2: 노드 고도화
- [ ] classify_node 프롬프트 튜닝 (엣지 케이스 테스트)
- [ ] chat_node 프롬프트 튜닝 (리뷰 컨텍스트 활용 품질 개선)
- [ ] 대화 이력(멀티턴) 지원 확인 및 개선

### Phase 3: Streamlit UI 완성
- [ ] 사이드바 필터가 실제 노드에 전달되는지 확인
- [ ] 응답에 참고한 리뷰 출처 표시 (st.expander)
- [ ] 에러 핸들링 (API 키 없음, DB 연결 실패 등)
- [ ] UI 스타일링 및 사용성 개선

### Phase 4: 통합 & 배포
- [ ] 현종/재훈 노드 통합 후 그래프 엔드투엔드 테스트
- [ ] `.streamlit/secrets.toml` 구성 (로컬 테스트용)
- [ ] `requirements.txt` 업데이트 (langgraph, langchain 등)
- [ ] Streamlit Cloud 배포
- [ ] Streamlit Cloud Secrets 설정 (OPENAI_API_KEY, MONGODB_URI)
- [ ] 배포 URL 확인 및 팀 공유

---

## 현종 (RAG Review Node)

### 구현 파일: `chatbot/nodes/rag_review_node.py`

- [ ] MongoDB 연결 설정 (`database/mongodb_connection.py` 활용)
- [ ] 사용자 질문에서 키워드 추출 로직 구현
- [ ] MongoDB에서 리뷰 검색 쿼리 구현 (text search 또는 벡터 유사도)
- [ ] `site_filter` 적용하여 사이트별 필터링
- [ ] 검색 결과를 `review_context` 문자열로 포맷팅
- [ ] 검색 결과 개수 제한 (토큰 초과 방지, 상위 5~10개 권장)
- [ ] 노드 단위 테스트 작성

### 참고
- DB: `review_db` 데이터베이스
- 컬렉션: `reviews_imdb`, `reviews_metacritic`, `reviews_rottentomatoes`
- 전처리 컬렉션: `preprocessed_reviews_*` (rating, date, content, Extreme_score, review_vector)
- 반환 형식: `{"review_context": "검색된 리뷰 문자열"}`

---

## 재훈 (Subject Info Node)

### 구현 파일: `chatbot/nodes/subject_info_node.py`

- [ ] 기생충 영화 정보 데이터 수집/정리
  - 감독: 봉준호
  - 출연: 송강호, 이선균, 조여정, 최우식, 박소담, 장혜진, 이정은, 박명훈
  - 수상: 아카데미 작품상/감독상/각본상/국제장편영화상 (2020)
  - 칸 황금종려상 (2019)
  - 장르, 개봉일, 러닝타임, 줄거리 등
- [ ] 사용자 질문에서 필요한 정보 유형 판단 로직
- [ ] 정보를 `subject_context` 문자열로 포맷팅
- [ ] (선택) 외부 API 연동 (TMDb, OMDb 등)
- [ ] 노드 단위 테스트 작성

### 참고
- 반환 형식: `{"subject_context": "영화 정보 문자열"}`
- 하드코딩 or API 중 선택 가능

---

## 공통

- [ ] `.env`에 `OPENAI_API_KEY` 추가
- [ ] 각자 브랜치에서 작업 후 PR → main 머지
- [ ] 통합 테스트 (전체 그래프 동작 확인)
