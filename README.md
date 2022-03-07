# 담다 EV

Damda EV Component

![HACS][hacs-shield]
![Version v1.4][version-shield]

문의 : 네이버 [HomeAssistant카페](https://cafe.naver.com/koreassistant)

## 담다 EV가 도움이 되셨나요?

<a href="https://qr.kakaopay.com/281006011000098177846177" target="_blank"><img src="https://github.com/GuGu927/damda_pad/blob/main/images/kakao.png" alt="KaKao"></a>

카카오페이 : https://qr.kakaopay.com/281006011000098177846177

<a href="https://paypal.me/rangee927" target="_blank"><img src="https://www.paypalobjects.com/webstatic/en_US/i/buttons/PP_logo_h_150x38.png" alt="PayPal"></a>

<a href="https://www.buymeacoffee.com/rangee" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/white_img.png" alt="Buy Me A Coffee"></a>

## 버전 기록정보

| 버전   | 날짜       | 내용                                                                    |
| ------ | ---------- | ----------------------------------------------------------------------- |
| v1.0.0 | 2021.11.11 | 게시                                                                    |
| v1.1.0 | 2021.12.05 | HA시작 속도에 영향을 주지 않도록 수정<br>기타 버그 수정                 |
| v1.1.2 | 2021.12.06 | 충전,과점유,주차 시간 표시방법을 `x:xx:xx`에서 `x일 x시간 x분`으로 변경 |
| v1.2.0 | 2021.12.08 | api호출 방식 변경 및 부분 리뉴얼로 인해 `재설치`를 권장합니다.          |
| v1.2.1 | 2021.12.11 | 상태반영 버그 수정 및 오류 수정<br>히스토리 그래프 관련 수정            |
| v1.2.2 | 2021.12.12 | 2021.12 버전 업데이트 대응                                              |
| v1.2.3 | 2021.12.12 | 다수 충전소 등록 시 발생하는 오류 수정                                  |
| v1.2.4 | 2021.12.15 | 2021.12 업데이트 대응                                                   |
| v1.2.5 | 2021.12.23 | 통계그래프 가능하게끔 수정                                              |
| v1.2.6 | 2022.01.04 | 오류 수정                                                               |
| v1.2.7 | 2022.03.07 | 2022.3 업데이트 대응(sensor 의 datetime/time deprecated 관련)           |

<br/>

## 준비물

- HomeAssistant `최신버전`(**2021.12.0 이상**)
- HomeAssistant OS, Core, Container 등 아무런 상관이 없습니다.

<br/>

## 사용자 구성요소를 HA에 설치하는 방법

### HACS

- HACS > Integrations > 우측상단 메뉴 > `Custom repositories` 선택
- `Add custom repository URL`에 `https://github.com/GuGu927/damda_evcharger` 입력
- Category는 `Integration` 선택 후 `ADD` 클릭
- HACS > Integrations 에서 `Damda EV` 찾아서 설치
- HomeAssistant 재시작

<br/>

### 수동설치

- `https://github.com/GuGu927/damda_evcharger` 페이지에서 `Code/Download ZIP` 을 눌러 파일을 다운로드, 내부의 `damda_evcharger` 폴더 확인
- HomeAssistant 설정폴더인 `/config` 내부에 `custom_components` 폴더를 생성(이미 있으면 다음 단계)<br/>설정폴더는 `configuration.yaml` 파일이 있는 폴더를 의미합니다.<br>
- `/config/custom_components`에 위에서 다운받은 `damda_evcharger` 폴더를 넣기<br>
- HomeAssistant 재시작

<br/>

## 담다EV를 설치하기 전 선행과정

### 공공데이터포털 회원가입 및 API키 발급받기

- [공공데이터포털](https://www.data.go.kr/) 에서 회원가입
- API 활용신청하기
- [한국환경공단\_전기자동차 충전소 정보](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15076352) 활용신청
- API키 확인(API키는 1회원 당 1개로 같은 API키로 여러개의 서비스를 호출 가능합니다.)

### 전기차충전소 이름 검색

- [무공해차 통합누리집](https://www.ev.or.kr/evmonitor) 에서 측정소명을 검색
- [한국환경공단](https://www.keco.or.kr/kr/sub/public/ev/step01/index.do) 에서 측정소명을 검색 혹은 엑셀다운로드 후 검색

<br/>

## 담다EV를 통합구성요소로 설치하는 방법

### 통합구성요소

- HomeAssistant 사이드패널 > 설정 > 통합 구성요소 > 통합 구성요소 추가<br>
- 검색창에서 `담다 EV` 입력 후 선택<br>
- API key에는 공공데이터포털에서 발급받은 API 키를 입력.
- Station name에는 위에서 찾은 측정소명을 입력.

[version-shield]: https://img.shields.io/badge/version-v1.2.7-orange.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg
