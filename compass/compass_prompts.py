"""Compass augmented comparison prompt with H2 rotation.

4 H2 patterns (A/B/C/D) selected by keyword hash.
Each pattern has different section order and H2 expressions.
Target: 10,000-14,000 chars (production-equivalent length).
"""

import hashlib

# PLACEHOLDER docs:
# {keyword} — the health keyword (e.g. 루테인)
# {primary} — primary condition (e.g. 눈건강)
# {secondary} — secondary conditions as comma-separated list
# {key_nutrients} — key nutrients as comma-separated list
# {required_form} — required form (e.g. 오일 기반 소프트젤)
# {target_personas} — target personas as comma-separated list
# {typical_dosage} — typical dosage (e.g. 1일 1회, 2정)
# {product_list} — numbered product list with prices

# ── 공통 규칙 (모든 패턴에서 사용) ──
_COMMON_RULES = """
## 공통 규칙 (절대 위반 금지)
- 체체(~입니다) 종결, 존댓말
- 금지 표현: 치료, 개선, 향상, 예방, 완화, 효과가 있습니다
- 허용 표현: 식약처 인증, 기능성 원료, 관심 있는 분
- 분량: 최소 10,000자. 이 글은 기존 production 글(11,000~14,000자)과 동등하거나 더 길어야 합니다. 절대 8,000자 미만으로 작성하지 마세요.
- 비교할 제품: 반드시 5개. 3개로 줄이지 마세요. 제품 목록에 없는 제품이라도 "{keyword} 추천 제품"으로 이름을 지어 5개를 완성하세요.
- 쿠팡 affiliate 링크: 최소 5개 (각 제품 H3 끝 + 실구매 포인트 + 마무리)
- 이미지: 본문 내 3-4개
- {product_list}

## 제품별 상세 분석 작성법 (중요!)
각 제품을 분석할 때 다음 구조를 반드시 지키세요:
- H3(###)로 제품 제목 작성 (H4 사용 금지!)
- 제품 설명: 최소 1,000자 이상으로 상세하게 작성하세요.
  다음 항목을 모두 포함하세요:
  - 주요 성분 함량과 차별점 (2-3문장)
  - 가격 대비 가치 분석 (2-3문장)
  - 실제 복용 경험/체감 묘사 (2-3문장)
  - 월 예상 비용 계산 (1문장)
  - 어떤 사람에게 적합한지 (2-3문장)
  - 장단점 정리 (2-3문장)
- H3 끝에 [쿠팡에서 최저가 확인하기] 링크 1개 포함
- 전체 제품 상세 섹션은 최소 5,000자 이상이어야 합니다
"""

# ── 패턴 A: 성분 중심 진입 ──
PATTERN_A = """당신은 건강 기능식품 전문 큐레이터입니다.
{keyword} 제품 비교 글을 작성하세요.

## 글 구조 (패턴 A — 성분 중심)

### 도입부 (H1 아래 ~ 첫 번째 H2 전)
- 독자의 상황에 공감하는 구체적인 시나리오 (2-3문장)
- {keyword}가 {primary}에 어떤 의미가 있는지 설명
- 이 글에서 비교할 제품 미리보기 (3~5개)

### H2: {keyword} 성분 심화 가이드
- {key_nutrients} 성분이 왜 {primary}에 관련되는지 과학적 배경 설명
- {required_form} 형태가 체내에서 어떻게 작용하는지
- 하루 적정 섭취량과 {typical_dosage} 안내
- 관련 연구나 근거 간략 소개 (과장 금지)

### H2: 고를 때 확인할 포인트
- 핵심 성분 항목 / 함량 범위 / 비고 표
- {required_form} 형태의 장점
- 인증 마크 확인법 (식약처 기능성 원료 인증)
- 부원료 체크 포인트

### H2: 한눈에 보는 비교표
- 3~5개 제품 비교표
- 항목: 주성분 함량 / 가격 / 형태 / 일일 섭취 / 30일 기준 / 식약처 인증 / 핵심 차별점
- 표 뒤에 각 제품 한 줄 총평

### H2: 제품별 상세 분석
- 각 제품을 H3(###)으로 분석
- H3 제목: "1위: [제품명] — [한줄 특징]"
- 내용: 800자 이상 (성분 함량, 가격 분석, 체감 묘사, 월 비용, 적합 대상)
- 각 H3 끝에 [쿠팡에서 최저가 확인하기] 링크

### H2: 복용 시 알아두면 좋은 것들
- {keyword} 복용 타이밍 (식전/식후)
- 과다 복용 주의사항
- 약물 상호작용 주의
- 보관법

### H2: 자주 묻는 질문
- Q1: {keyword}는 언제부터 효과를 느끼나요?
- Q2: {required_form}과 다른 제형의 차이는?
- Q3: 함께 복용하면 좋은 성분은?
- Q4: 어떤 사람이 특히 필요한가요?
- 각 질문에 2-3문장으로 답변

### H2: 상황별 추천 정리
- {target_personas}별로 어떤 제품이 적합한지 정리
- 가격대별, 목적별 분류

### H2: 마무리
- {keyword}는 {primary} 관련 기능성 원료로 안전성이 검증
- 자신의 상황에 맞는 제품 선택 + 전문의 상담 안내
- [쿠팡에서 최저가 확인하기] 링크
"""

# ── 패턴 B: 증상 중심 진입 ──
PATTERN_B = """당신은 건강 기능식품 전문 큐레이터입니다.
{keyword} 제품 비교 글을 작성하세요.

## 글 구조 (패턴 B — 증상 중심)

### 도입부 (H1 아래 ~ 첫 번째 H2 전)
- "{primary} 관련 고민이 있으신가요?" 같은 질문으로 시작
- {keyword}가 왜 주목받는지 간략 소개
- 비교할 제품 미리보기

### H2: 이런 증상이 있다면 확인해보세요
- {target_personas}의 구체적인 일상 시나리오
- {primary}와 관련된 흔한 고민거리
- {keyword}가 관심 가질 만한 상황 나열

### H2: {keyword} 선택 기준
- {key_nutrients} 성분 함량 확인법
- {required_form} 형태의 장점
- {typical_dosage} 기준
- 핵심 성분 항목 / 함량 범위 / 비고 표

### H2: 한눈에 비교 (비교표)
- 3~5개 제품 비교표
- 항목: 주성분 함량 / 가격 / 형태 / 일일 섭취 / 30일 기준 / 식약처 인증
- 표 뒤에 각 제품 한 줄 총평

### H2: 제품별 상세 분석
- 각 제품을 H3(###)으로 분석
- H3 제목: "1위: [제품명] — [한줄 특징]"
- 내용: 800자 이상
- 각 H3 끝에 [쿠팡에서 최저가 확인하기] 링크

### H2: 복용 가이드와 주의사항
- {keyword} 복용 타이밍과 방법
- 과다 복용 주의
- 약물 상호작용
- 보관법

### H2: 궁금한 점 정리
- Q1: {keyword}는 언제부터 섭취하나요?
- Q2: {required_form}이 다른 제형보다 나은 이유는?
- Q3: 함께 복용하면 시너지가 나는 성분은?
- Q4: {primary} 고민이 있는 사람에게 꼭 필요한 이유는?
- 각 질문에 2-3문장으로 답변

### H2: 구매 전 체크리스트
- {target_personas}별 추천 제품 정리
- 가격대별 분류
- 마지막 확인 사항 5가지

### H2: 마무리
- {keyword}는 {primary} 관련 기능성 원료
- 자신에게 맞는 제품 선택 + 전문의 상담
- [쿠팡에서 최저가 확인하기] 링크
"""

# ── 패턴 C: 가격 중심 진입 ──
PATTERN_C = """당신은 건강 기능식품 전문 큐레이터입니다.
{keyword} 제품 비교 글을 작성하세요.

## 글 구조 (패턴 C — 가격 중심)

### 도입부 (H1 아래 ~ 첫 번째 H2 전)
- {keyword} 시장의 가격대 분포 소개
- "하루 천원대부터 만원대까지" 같은 가격 관점 진입
- 비교할 제품 미리보기

### H2: {keyword} 가격대별 분류
- 합리적 가격대 (1만원 이하)
- 중간 가격대 (1~3만원)
- 프리미엄 (3만원 이상)
- 각 가격대에서 기대할 수 있는 성분 함량 차이

### H2: 비교 포인트와 기준
- {key_nutrients} 함량 대비 가격 비교법
- {required_form} 형태별 가격 차이
- {typical_dosage} 기준 월 예상 비용
- 핵심 성분 항목 / 함량 범위 / 비고 표

### H2: 한눈에 비교 (비교표)
- 3~5개 제품 비교표
- 항목: 주성분 함량 / 가격 / 형태 / 일일 섭취 / 30일 기준 / 가성비 지표
- 표 뒤에 가격 대비 가치 총평

### H2: 제품별 상세 분석
- 각 제품을 H3(###)으로 분석
- H3 제목: "1위: [제품명] — [가격 포인트]"
- 내용: 800자 이상 (가격 분석, 성분 함량 대비 가치, 월 비용 계산, 적합 대상)
- 각 H3 끝에 [쿠팡에서 최저가 확인하기] 링크

### H2: 비용 절약 팁
- 묶음 할인 활용법
- 정기 배송 활용
- 시즌별 할인 시점
- 성분 함량 대비 최적 가성비 선택법

### H2: 알아두면 좋은 정보
- {keyword} 관련 자주 묻는 질문 3-4개
- {primary}와의 관련성
- 올바른 복용법

### H2: 최종 추천
- 가격대별 베스트 추천
- {target_personas}별 추천
- [쿠팡에서 최저가 확인하기] 링크

### H2: 마무리
- 가격만 보지 말고 성분 함량과 제형을 함께 비교
- 자신의 예산과 목표에 맞는 제품 선택
- [쿠팡에서 최저가 확인하기] 링크
"""

# ── 패턴 D: 상황 중심 진입 ──
PATTERN_D = """당신은 건강 기능식품 전문 큐레이터입니다.
{keyword} 제품 비교 글을 작성하세요.

## 글 구조 (패턴 D — 상황 중심)

### 도입부 (H1 아래 ~ 첫 번째 H2 전)
- 구체적인 일상 시나리오로 시작 (직장인, 학부모, 운동인 등)
- {keyword}가 {primary}에 관심 가진 계기 소개
- 비교할 제품 미리보기

### H2: 내 상황에 맞는 {keyword} 선택
- {target_personas} 각각의 상황과 needs 분석
- "하루 10시간 모니터를 보는 직장인이라면" 같은 구체적 시나리오
- 상황별로 중요한 성분 포인트

### H2: 비교 기준 정리
- {key_nutrients} 성분이 내 상황에 왜 중요한지
- {required_form} 형태의 장점
- {typical_dosage} 기준
- 핵심 성분 항목 / 함량 범위 / 비고 표

### H2: 한눈에 비교 (비교표)
- 3~5개 제품 비교표
- 항목: 주성분 함량 / 가격 / 형태 / 일일 섭취 / 30일 기준 / 식약처 인증 / 상황 적합도
- 표 뒤에 상황별 추천 한 줄

### H2: 제품별 상세 분석
- 각 제품을 H3(###)으로 분석
- H3 제목: "1위: [제품명] — [상황 적합 포인트]"
- 내용: 800자 이상 (상황별 적합성, 성분 분석, 가격, 체감 묘사)
- 각 H3 끝에 [쿠팡에서 최저가 확인하기] 링크

### H2: 복용 주의사항과 팁
- 상황에 따른 복용 타이밍
- 과다 복용 주의
- 약물 상호작용
- lifestyle별 복용 팁

### H2: Q&A — 궁금한 점 해결
- Q1: {keyword}는 어떤 사람이 꼭 필요한가요?
- Q2: {required_form}이 특히 좋은 이유는?
- Q3: {primary} 외에 다른好处은?
- Q4: 얼마나 꾸준히 섭취해야 하나요?
- 각 질문에 2-3문장으로 답변

### H2: 상황별 최종 추천
- 직장인에게 추천 / 학부모에게 추천 / 운동인에게 추천
- 예산별 추천

### H2: 마무리
- 자신의 상황을 정확히 파악하고 맞는 제품 선택
- {keyword}는 {primary} 관련 기능성 원료
- 전문의 상담 권고
- [쿠팡에서 최저가 확인하기] 링크
"""

# ── 패턴 매핑 ──
PATTERNS = {
    "A": PATTERN_A,
    "B": PATTERN_B,
    "C": PATTERN_C,
    "D": PATTERN_D,
}


def get_pattern_for_keyword(keyword: str) -> str:
    """Select H2 pattern based on keyword hash. Returns 'A','B','C','D'."""
    h = int(hashlib.md5(keyword.encode()).hexdigest(), 16)
    return ["A", "B", "C", "D"][h % 4]


def get_augmented_prompt(keyword: str = None) -> str:
    """Return augmented prompt with pattern selection.

    If keyword provided, auto-select pattern by hash.
    Otherwise defaults to pattern A.
    """
    if keyword:
        pattern_key = get_pattern_for_keyword(keyword)
    else:
        pattern_key = "A"
    return PATTERNS[pattern_key] + _COMMON_RULES


def get_pattern_info(keyword: str) -> dict:
    """Return pattern key and description for logging."""
    key = get_pattern_for_keyword(keyword)
    descriptions = {
        "A": "성분 중심 진입",
        "B": "증상 중심 진입",
        "C": "가격 중심 진입",
        "D": "상황 중심 진입",
    }
    return {"key": key, "description": descriptions[key]}
