# 컴퍼스 모드 (Compass Mode)

독립된 글쓰기 파이프라인. 기존 파이프라인과 완전히 분리되어 동작합니다.

## 개요

컴퍼스 모드는 기존 health-hugo 파이프라인과 별도로 동작하는 실험적 글쓰기 모드입니다.
기존 파이프라인을 교체하기 전, 새로운 글 구조와 모드를 안전하게 검증하기 위해 만들어졌습니다.

## 핵심 원칙

1. **완전한 분리** — 기존 파이프라인 파일( writer.py, scheduler.py 등)을 전혀 수정하지 않음
2. **수동 실행만** — 스케줄러/크론에 등록하지 않음, 사람이 직접 실행
3. **content/posts/ 미사용** — 글은 `compass/output/drafts/`에만 저장, Hugo 빌드에 포함 안 됨
4. **LLM 호출은 OK** — `shared.ai_writer.generate()` 사용 가능 (read-only 공유 유틸)
5. **writer.py 함수 호출 불가** — `shared/`에 없으면 compass 내부에 자체 fallback 구현

## 모드 (3개)

| 모드 | 설명 | 진입점 |
|------|------|--------|
| ingredient_dive | 특정 성분 중심 해설 → 제품 추천 | 성분 해부 |
| symptom_care | 증상 기반 진입 → 상황별 추천 | 이런 증상이라면 |
| versus | 제품 2개 1:1 심층 비교 | A vs B |

## 사용법

```bash
# 단일 모드 실행
python3 compass/compass_runner.py --keyword "루테인" --mode symptom_care

# 3개 모드 모두 실행
python3 compass/compass_runner.py --keyword "루테인" --mode all

# 평가만 실행
python3 compass/compass_runner.py --evaluate compass/output/drafts/루테인-symptom_care.md

# 실 LLM 사용
python3 compass/compass_runner.py --keyword "루테인" --mode versus --real-llm
```

## 디렉토리 구조

```
health-hugo/
├── compass/
│   ├── compass_runner.py        # 단독 실행 진입점
│   ├── compass_prompts.py       # 모드별 프롬프트 템플릿
│   ├── compass_generator.py     # LLM 호출 + 글 생성
│   ├── compass_post_processor.py # 독자적 후처리
│   ├── compass_evaluator.py     # 결과물 품질 자동 평가
│   ├── config/
│   │   └── modes.yaml           # 모드 정의
│   └── output/
│       ├── drafts/              # 생성된 글 (content/posts에 넣지 않음)
│       └── evaluated/           # 평가 결과
├── pipelines/curation/          # 기존 파이프라인 (수정 금지)
├── content/posts/               # 기존 발행 글 (수정 금지)
└── ...
```

## 자동 평가 기준

`compass_evaluator.py`가 생성된 글에 대해 5가지 항목을 자동 평가합니다:

| 항목 | 설명 | 기준 |
|------|------|------|
| (a) Compliance | 효능 단정 주장 | 0 violations (PASS) |
| (b) Structure Entropy | H2 구조 다양성 | ≥ 2.34 (baseline 2.44 - 0.1) |
| (c) Affiliate Slots | 쿠팡 링크 삽입 위치 | ≥ 2개 |
| (d) Readability | H2 수, 문단 길이, 본문 길이 | H2≥3, avg_para≥2.0, total≥500 |
| (e) Similarity | 기존 글과의 유사도 | < 0.5 |

## 교체 기준 (기존 파이프라인 교체 시)

컴퍼스 모드가 기존 파이프라인을 교체하는 조건:

1. **30편 이상 생성 + 평가** — 충분한 데이터 축적
2. **Compliance 100% PASS** — 효죄 주장이 전혀 없어야 함
3. **Entropy ≥ 2.5** — 기존보다 구조적 다양성 높아야 함
4. **수동 리뷰 10편 이상 통과** — 사람이 직접 검토
5. **CTR/RPM 비교** — 기존 대비 광고 수익 하락 없어야 함

이 조건이 모두 충족되면 그때 기존 파이프라인 교체 논의를 시작합니다.
이 기준은 운영진과 공유하여 합의된 후 적용됩니다.

## 출력 파일

```
compass/output/drafts/{keyword}-{mode}.md      # 생성된 글
compass/output/evaluated/{keyword}-{mode}.json  # 평가 결과
```

## 주의사항

- `compass/output/`에만 글 저장
- `content/posts/`에는 절대 글을 넣지 않음
- Hugo 빌드에 포함되지 않음
- 실발행되지 않음 (평가 전용)
