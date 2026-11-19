# Algorithm Overview

## 전체 흐름
1. GPS CSV 로드
2. PosX/PosY 또는 Latitude/Longitude 자동 인식
3. 1Hz 기준 GPS 정제
4. 도로 노드/엣지로 그래프 구성
5. BallTree 기반 후보 탐색
6. emission / transition probability 계산
7. Viterbi로 최적 경로 추정
8. 최종 경로를 node / geojson / html로 저장

## Strict transition의 핵심
- rd/gd 비율 과도 시 차단
- 정지 근처의 큰 도로 점프 차단
- 시간 대비 과도한 도로 이동 속도 차단
- heading이 크게 반대 방향이면 차단
