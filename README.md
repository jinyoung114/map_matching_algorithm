# Strict Map Matching Project

## 1. 프로젝트 개요
이 프로젝트는 GPS 데이터를 도로 네트워크에 정합시키는 **Strict Map Matching** 코드입니다.

주요 특징:
- 1Hz GPS 정제
- BallTree 기반 후보 탐색
- 거리 / 속도 / 방향 제약을 반영한 strict transition probability
- Viterbi 기반 최적 경로 추정
- 도로 edge의 WKT geometry를 활용한 실제 도로 경로 생성
- GeoJSON / HTML / CSV 결과 저장

이 코드는 **배치형 map matching** 코드입니다.
즉, 의사 실시간 sliding window 방식이 아니라, 정제된 전체 GPS 시퀀스를 대상으로 한 번에 맵매칭을 수행합니다.

---

## 2. 폴더 구조

```text
strict_map_matching_project/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ input/
│  │  ├─ 충남70자1265_0430_filtered.csv
│  │  ├─ mm_nodes_dense_27_33.csv
│  │  └─ mm_edges_dense_27_33.csv
│  ├─ output/
│  └─ examples/
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ utils.py
│  ├─ gps_processing.py
│  ├─ road_network.py
│  ├─ candidates.py
│  ├─ transition.py
│  ├─ viterbi.py
│  ├─ outputs.py
│  └─ pipeline.py
├─ scripts/
│  └─ run_strict_map_matching.py
└─ docs/
   ├─ algorithm_overview.md
   ├─ handover_notes.md
   └─ output_description.md
```

---

## 3. 입력 파일

`data/input/` 폴더에 아래 파일을 넣으면 됩니다.

- `충남70자1265_0430_filtered.csv` : GPS 데이터
- `mm_nodes_dense_27_33.csv` : 도로 노드 CSV
- `mm_edges_dense_27_33.csv` : 도로 엣지 CSV

파일명을 바꾸고 싶으면 `src/config.py`에서 같이 수정해야 합니다.

---

## 4. 실행 환경

### Python
- Python 3.10 이상 권장

### 설치
```bash
pip install -r requirements.txt
```

---

## 5. 실행 방법

### 1) 프로젝트 폴더로 이동
```bash
cd C:\Users\jinyo\Downloads\strict_map_matching_project
```

### 2) 가상환경 생성 (처음 1회)
```bash
python -m venv venv
```

### 3) 가상환경 활성화
PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
venv\Scripts\activate
```

### 4) 패키지 설치
```bash
pip install -r requirements.txt
```

### 5) 실행
```bash
python scripts/run_strict_map_matching.py
```

---

## 6. 출력 결과

실행 후 `data/output/` 폴더에 아래 결과가 생성됩니다.

- `strict_matched_gps_cleaned.csv`
  - GPS 정제 결과
- `strict_matched_strict_raw.csv`
  - Viterbi 최종 후보 시퀀스
- `strict_matched_path_nodes.csv`
  - 최종 노드 경로
- `strict_matched_route.geojson`
  - 실제 도로 geometry 기반 최종 경로
- `strict_matched_map_only.html`
  - 맵매칭 경로 시각화 결과

---

## 7. 알고리즘 흐름

```text
GPS 로드 및 정제
→ 도로망 그래프 생성
→ 후보 노드 탐색 (BallTree)
→ emission probability 계산
→ transition probability 계산 (strict constraint)
→ Viterbi로 최적 경로 추정
→ path nodes / geojson / html 저장
```

---

## 8. 핵심 파라미터

`src/config.py`에서 수정 가능:

- `GPS_FILE`
- `NODES_FILE`
- `EDGES_FILE`
- `OUTPUT_PREFIX`
- 후보 반경
- 커브 구간 반경
- sigma 값
- speed threshold
- heading threshold
- transition constraint 값

---

## 9. 코드 수정 시 먼저 보면 좋은 파일

1. `src/config.py`
2. `src/pipeline.py`
3. `src/gps_processing.py`
4. `src/transition.py`
5. `src/viterbi.py`
6. `src/outputs.py`

---

## 10. 인수인계 메모

- 이 코드는 전체 trajectory를 대상으로 수행하는 strict map matching 코드입니다.
- 의사실시간 sliding window 방식과 다릅니다.
- GPS 전처리 품질에 따라 결과 차이가 큽니다.
- 도로 네트워크 연결성이 부족하면 shortest path가 자주 끊길 수 있습니다.
- 엣지 geometry(WKT)가 있으면 더 자연스러운 경로를 만들 수 있습니다.
- 결과 확인은 `data/output/strict_matched_map_only.html`부터 보면 됩니다.
