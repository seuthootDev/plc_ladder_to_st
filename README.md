# PLC Ladder → ST / Ladder Viewer PoC

Mitsubishi GX Works2 프로젝트(`plc project_260626`, Q06H)의 **래더 로직**을  
PDF + IL CSV에서 추출해 **Structured Text(ST)** 로 변환하고, ST를 기준으로 **SVG/HTML 래더 뷰어**를 생성하는 파이프라인입니다.

**핵심 목표**

- ST를 가상 환경에서 편집·검토할 수 있는 **편집 표면(edit surface)** 으로 사용
- 래더 뷰어로 GX Works2 / PDF와 대조하며 로직 검증
- 검증된 ST 변경을 현장 PLC에 반영하는 흐름을 PoC로 검증

---

## 파이프라인 개요

```
PDF + IL CSV
    │
    ▼  prepare
context JSON  (plc_export/context/)
    │
    ▼  generate_st
ST 파일       (plc_export/st/)          ← 편집·검증의 기준점
    │
    ├─ verify (rung/step 수 대조)
    │
    ├─ Logic track ──► plc_export/ladder/     (규칙 기반 SVG/HTML)
    │
    └─ AI track    ──► plc_export/ladder_ai/  (Gemini API SVG/HTML)
```

| 단계 | 모듈 | 입력 | 출력 |
|------|------|------|------|
| 1. prepare | `prepare.py` | `csv/`, `12314.pdf` | `plc_export/context/` |
| 2. generate_st | `generate_st.py` | context JSON | `plc_export/st/P*.st` |
| 3. verify | `verify.py` | context + ST | 콘솔 리포트 |
| 4. render_ladder | `render_ladder.py` | ST | `plc_export/ladder/` |
| 5. render_ladder_ai | `render_ladder_ai.py` | ST + Gemini API | `plc_export/ladder_ai/` |

> **CSV/PDF는 ST 생성 시에만 사용**합니다. 래더 렌더링(Logic/AI track)은 **ST만** 읽습니다.

---

## Two-Track: ST → 래더

동일한 ST를 두 가지 방식으로 시각화합니다.

| | Logic track | AI track |
|---|-------------|----------|
| 모듈 | `ladder_layout.py` + `ladder_renderer.py` | `ai_ladder.py` |
| 방식 | BoolExpr 패턴 매칭 → 좌표 레이아웃 → SVG | Gemini가 ST+패턴 가이드 → SVG 직접 생성 |
| 출력 | `plc_export/ladder/` | `plc_export/ladder_ai/` |
| 일관성 | 높음 (픽셀·폰트 고정) | 중간 (프롬프트+패턴 topology 가이드) |
| API 키 | 불필요 | 필요 |

Logic track은 `ladder_layout.py`의 `_layout_*` 핸들러로 ORB/ANB/MPS/3레일 분기 등을 규칙 기반 배치합니다.  
AI track은 하드룰 프롬프트 + **분기 패턴 카탈로그 topology**를 rung마다 주입해 변동성을 줄입니다.

---

## 대상 프로그램 (12개)

| POU | 이름 | 비고 |
|-----|------|------|
| P01_Main | Main | rung 다수 |
| P02_Lamp | Lamp | OR/중첩 분기 예제 |
| P10_PrimerVision | Primer Vision | |
| P11_SealerVision | Sealer Vision | |
| P12_BodyVision | Body Vision | |
| P20_PrimerRobot | Primer Robot | |
| P21_BodyRobot | Body Robot | |
| P30_Centering | Centering | MPS 분기 |
| P31_Sealer | Sealer | |
| P32_Primer | Primer | |
| P33_Gripper | Gripper | 그리퍼 ORB |
| P99_Error | Error | 3레일 ORB, 복잡 분기 |

---

## 디렉터리 구조

```
plc/
├── main.py                 # 전체 파이프라인 진입점
├── requirements.txt
├── .env.example            # Gemini API 키 템플릿
├── .env / .env.local       # API 키 (git 제외)
├── 12314.pdf               # GX Works2 Project Listing PDF
├── 12314_extracted.txt     # PDF 텍스트 추출본 (prepare 대체 소스)
├── csv/                    # IL CSV 12개 (초기 변환용)
├── plc_converter/          # Python 엔진
│   ├── prepare.py          # PDF+CSV → context
│   ├── generate_st.py      # context → ST
│   ├── verify.py           # rung/step 검증
│   ├── st_parser.py        # ST → ProgramIR / BoolExpr
│   ├── ladder_layout.py    # BoolExpr → 레이아웃 (Logic track)
│   ├── ladder_renderer.py  # 레이아웃 → SVG
│   ├── render_ladder.py    # Logic track CLI
│   ├── ai_ladder.py        # Gemini ST→SVG (AI track)
│   ├── render_ladder_ai.py # AI track CLI
│   ├── ladder_patterns/    # 분기 패턴 카탈로그
│   │   ├── catalog.json    # 패턴 12종 topology 정의
│   │   ├── registry.py     # 패턴 분류 / 스캔
│   │   └── prompt_builder.py  # AI 프롬프트용 rung별 패턴 주입
│   └── paths.py            # 경로 상수
└── plc_export/
    ├── context/            # 중간 JSON (programs/, device_comments 등)
    ├── st/                 # 생성·편집용 ST
    │   └── codesys/        # CODESYS 붙여넣기용 declaration/implementation 분리
    ├── ladder/             # Logic track SVG/HTML
    └── ladder_ai/          # AI track SVG/HTML
```

---

## 설치

```powershell
cd plc
python -m venv .venv          # 선택
.\.venv\Scripts\activate      # 선택

pip install -r requirements.txt
```

의존성:

- `pymupdf` — PDF 파싱
- `python-dotenv` — `.env` / `.env.local` 로드
- `google-genai` — AI track (Gemini API)

---

## 환경 변수

`.env.example`을 복사해 키를 설정합니다.

```powershell
copy .env.example .env
# 또는 .env.local 사용 (ai_ladder.py가 둘 다 읽음)
```

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `GEMINI_API_KEY` | Gemini API 키 | (필수, AI track) |
| `GOOGLE_API_KEY` | 위와 동일 (대체 이름) | |
| `GEMINI_MODEL` | 모델 이름 | `gemini-2.0-flash` |
| `GEMINI_RETRY_MAX` | 재시도 횟수 (`0`=무제한) | `0` |
| `GEMINI_RETRY_BASE_DELAY` | 첫 재시도 대기(초) | `10` |
| `GEMINI_RETRY_MAX_DELAY` | 최대 대기(초) | `120` |
| `GEMINI_REQUEST_DELAY` | 프로그램 간 간격(초) | `3` |

AI track은 503/429/네트워크 끊김 등 **일시 오류 시 성공할 때까지 재시도**합니다.  
이미 생성된 SVG는 `--ai-skip-existing` / `--skip-existing`으로 건너뛸 수 있습니다.

---

## 사용법

### 전체 파이프라인

```powershell
# Logic track만 (API 키 불필요)
python main.py

# Logic + AI track
python main.py --ai-ladder

# AI만 이어서 (이미 만든 SVG 건너뛰기)
python main.py --ai-ladder --ai-skip-existing

# verify 생략, SVG만 (HTML 없음)
python main.py --skip-verify --no-html
```

### 단계별 실행

```powershell
python -m plc_converter.prepare
python -m plc_converter.generate_st
python -m plc_converter.verify
python -m plc_converter.render_ladder --all
python -m plc_converter.render_ladder_ai --all --skip-existing
```

### Logic track (단일 파일)

```powershell
python -m plc_converter.render_ladder --st plc_export/st/P02_Lamp.st
python -m plc_converter.render_ladder --all
```

### AI track (단일 파일)

```powershell
python -m plc_converter.render_ladder_ai --st plc_export/st/P02_Lamp.st
python -m plc_converter.render_ladder_ai --all
```

### 분기 패턴 카탈로그

```powershell
# 패턴 12종 + 스타일 규격 목록
python -m plc_converter.ladder_patterns --list

# 12개 ST rung별 패턴 분류
python -m plc_converter.ladder_patterns --scan
```

패턴 topology 정의: `plc_converter/ladder_patterns/catalog.json`  
실제 좌표 배선: `plc_converter/ladder_layout.py`의 `layout_handler` 함수

#### 패턴 12종 (요약)

| pattern_id | 설명 |
|------------|------|
| `series_and` | 단순 직렬 AND |
| `parallel_or` | OR 병렬 합류 |
| `or_and_tail` | (A AND B) OR C |
| `and_or_tail` | (A AND B) OR C 변형 |
| `nested_or_in_and` | AND 안 중첩 OR |
| `head_fork_or` | ANB/ORB 머리 분기 |
| `triple_rail_orb_timer` | 3레일 ORB + 타이머 (P99) |
| `gripper_orb` | 그리퍼형 3레일 ORB |
| `sensor_mps_fork` | MPS 센서 분기 |
| `parallel_outputs` | 다중 출력 |
| `timer_on_branch` | 분기 타이머 |
| `set_rst` | SET / RST |

---

## ST 편집 워크플로

1. `plc_export/st/Pxx_*.st` 를 CODESYS 등에서 열어 IMPLEMENTATION 수정
2. `python -m plc_converter.render_ladder --st ...` 로 Logic track 뷰어 갱신
3. (선택) `python -m plc_converter.render_ladder_ai --st ...` 로 AI track 비교
4. PDF / GX Works2 래더와 대조
5. 현장 PLC에 반영

ST 구문은 `st_parser.py`가 이해하는 범위 내에서 동작합니다.  
새 패턴이 layout 핸들러에 없으면 generic 레이아웃으로 그려질 수 있습니다.

---

## 산출물 확인

- Logic: `plc_export/ladder/P02_Lamp.html` — 브라우저에서 열기
- AI: `plc_export/ladder_ai/P02_Lamp.html`
- SVG만 필요하면 `.svg` 파일 직접 열기

---

## 제한·알려진 이슈

- **Logic track**: 복잡 분기(P32, P33, P99 등)는 PDF와 그래픽 배선이 100% 일치하지 않을 수 있음. 로직 파악은 가능한 수준.
- **AI track**: rung 수가 많은 프로그램(P01, P21)은 API 응답이 수 분~십 수 분 걸릴 수 있음.
- **AI track**: API 한도(429) / 과부하(503) 시 자동 재시도. 한도 소진 시 다음날 재시도 또는 `--skip-existing`으로 이어하기.
- **Windows + 한글 경로**: `.py` 파일 편집 시 인코딩 깨짐(null byte)이 발생할 수 있음. Python 파일 수정 후 import 테스트 권장.

---

## 모듈 참고

| 파일 | 역할 |
|------|------|
| `csv_parser.py` | IL CSV 파싱 |
| `pdf_parser.py` / `pdf_reader.py` | PDF Listing 파싱 |
| `il_builder.py` | context → ProgramIR (IL 기반) |
| `st_generator.py` | ProgramIR → ST 텍스트 |
| `models.py` | `BoolExpr`, `Rung`, `ProgramIR` 등 |
| `device_utils.py` | 디바이스명/주석 유틸 |

---

## 라이선스 / 출처

- 원본: Mitsubishi GX Works2 프로젝트 `plc project_260626` (Q06H)
- PoC 목적의 내부 변환·뷰어 도구
