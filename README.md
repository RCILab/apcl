# APCL project page

APCL 프로젝트 홈페이지의 심사용 버전입니다. 저자·소속·연락처 표시와
특정 연구실 및 저장소로 연결되는 링크를 제외했습니다.
모든 프로젝트 자료는 상대 경로로 연결해 다른 정적 호스팅으로 옮길 수 있습니다.

## 미리 보기

`index.html`을 바로 열거나, 이 폴더에서 다음 명령을 실행하세요.

```powershell
python -B tools/serve.py
```

브라우저: <http://127.0.0.1:8765/>. 정적 HTML/CSS/JS이므로 별도 빌드나 Node.js가 필요 없습니다.
직접 파일로 열 때도 동영상과 도표 전환이 작동합니다. 자막은 HTTP 미리 보기를 권장합니다.
이 미리보기 서버는 동영상 탐색에 필요한 HTTP Range 요청을 지원합니다.
배포 ZIP을 풀어 확인할 때는 `python -B preview.py`를 사용하세요.

## 구성

- 첫 화면: 두 MuJoCo 로봇의 궤적과 접촉점 추정을 비교하는 무음 반복 영상, 재생/정지, reduced-motion 대응
- 핵심 원리: 두 힘 방향의 각도를 바꾸는 기하 그림
- 18초 설명 영상: 실제 입자 스냅샷, 영문 자막, MP4 다운로드
- 정량 결과: 1,200회 전체 / trust gate 통과 556회 전환, 정의·범위 표시
- 연구 코드·데이터·소개 PDF: 모두 TBD, 다운로드 링크 비활성화

## 근거와 범위

- 결과 원본: `../claude_try/results/main.jsonl`, SHA-256는 `static/data/results.json` 참조
- 영상: development seed 17을 2개 자세로 재실행한 실제 관절 궤적과 입자 분포
- 왼쪽 로봇은 CPF, 오른쪽은 APCL의 실제 관절 궤적을 각각 재생. 같은 초기 상태/접촉에서 각자 다음 자세를 선택
- 두 로봇은 비교를 위해 동일한 장면에 평행 이동해 배치한 독립 시행의 재생이며, 물리적인 협동 실험이 아님
- 금색 점은 실제 접촉점, 주황색·민트색 마름모는 각 방법의 가중평균 추정점. 위치를 과장하지 않고 표시 기호만 확대
- 시뮬레이션 시간 7초를 18초로 편집: 정지 구간과 감속 재생 포함
- 스냅샷 사이의 추론 과정을 임의로 보간하지 않음
- 화면의 물체 형상은 추정기에 주어지지 않음. 접촉은 물체 고정점에 적용한 외력이며 실제 pusher 충돌을 재현한 영상은 아님
- 하드웨어 실험은 미완료. 기존 논문 PDF의 임시 수치/미완성 부분은 이 사이트에 포함하지 않음
- 소스 `claude_try/`, 원고 `paper/`는 수정하지 않음

## 재생성

아래 영상·데이터 재생성 명령은 원래 연구 작업공간에서 실행합니다. 이 사이트 저장소만
clone한 경우 원본 형제 폴더 `claude_try/`, `gpt_try/`가 없으므로 실행되지 않습니다.
홈페이지 자체는 원본 작업공간이나 Python 설치 없이 동작합니다.
원본 자료는 로컬 작업공간의 `static/data/`, `static/downloads/`에 보관합니다.
현재 두 폴더는 Git 추적과 배포 ZIP에서 제외하며, 연구 자료 공개 상태는 TBD입니다.

작업공간 루트에서 실행합니다. Python 3.12, numpy, scipy, mujoco, Pillow, imageio-ffmpeg,
PyMuPDF가 필요합니다. 렌더링 스크립트는 Windows Segoe UI 글꼴을 사용합니다.

```powershell
python -B apcl/tools/capture_episode.py
python -B apcl/tools/prepare_results.py
python -B apcl/tools/render_video.py
python -B apcl/tools/make_note.py
python -B apcl/tools/package_site.py
```

렌더링에 필요한 Franka FR3 시각 메시를 MuJoCo Menagerie에서 `apcl/.build/`로 내려받습니다.
시각화 모형에는 단순화한 그리퍼 형상을 추가했으며, 궤적/추정 결과를 바꾸지는 않습니다.
`static/site.js`에는 직접 파일 열기를 위한 정량 결과 사본이 있습니다. 결과를 재생성할 때
`static/data/results.json`과 수치를 맞춘 뒤 `tools/validate_site.py`로 확인하세요.

## 배포용 파일

`apcl-site.zip`에는 `index.html`, `static/`, README와 로컬 확인용 `preview.py`가 포함됩니다.
TBD 상태인 자료 폴더(`static/data/`, `static/downloads/`)는 ZIP에 넣지 않습니다.
같은 내용의 `apcl-review.zip`도 생성합니다. 두 ZIP에는 Git 저장소나 커밋 이력이 포함되지 않습니다.
`tools/`, `.build/`, 가상환경과 원본 작업공간은 업로드할 필요가 없습니다.
ZIP 내부 `apcl/`을 웹 루트에 놓으면 `/apcl/` 경로에서 작동합니다.
공유용 이미지도 상대 경로를 사용하며 원래 호스팅 주소를 메타데이터에 넣지 않습니다.
실제 익명 제출 시에는 이 파일 묶음을 별도로 올린 익명 공유 링크를 사용하세요.

## 외부 자산

MuJoCo Menagerie Franka FR3: `static/licenses/FR3-LICENSE.txt`.
`THIRD_PARTY.md`에 출처와 시각화 변경 사항을 기록했습니다.
