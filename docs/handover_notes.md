# Handover Notes

## 이 코드의 성격
- 전체 trajectory를 한 번에 맵매칭하는 strict map matching 코드
- pseudo realtime 코드와 다름

## 먼저 확인할 파일
1. src/config.py
2. src/gps_processing.py
3. src/transition.py
4. src/viterbi.py
5. src/outputs.py

## 수정 포인트
- GPS 컬럼 형식이 다르면 gps_processing.py 수정
- nodes / edges 컬럼명이 다르면 road_network.py 수정
- 후보 반경 조정은 candidates.py
- strict 제약 완화/강화는 transition.py

## 디버깅 순서
1. GPS 정제 후 점 수 확인
2. 후보 노드 개수 확인
3. shortest path 연결 여부 확인
4. transition가 과도하게 막히는지 확인
5. geojson/html 결과 확인
