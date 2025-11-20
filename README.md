# NCP REST Client

NAVER Cloud Platform(NCP)과 GOV-Ncloud 환경에서 동일하게 사용할 수 있는 인증/REST 모듈입니다.  
모든 Open API (예: server, vpc, monitoring 등)에 공통 서명을 붙여 호출할 수 있습니다.

## 구성 요소
- `ncp_client.auth.NCPRequestSigner` : Access/Secret Key로 HMAC-SHA256 서명과 필수 헤더를 생성
- `ncp_client.client.NCPApiClient` : `requests.Session`을 감싸 인증, GOV/Global base URL, 기본 헤더/리전을 관리
- `examples/basic_usage.py` : 환경 변수만 설정하면 바로 서버 리스트 조회 예제를 실행할 수 있는 스크립트

## 설치
```bash
pip install -e .
```

## 환경 변수
- `NCP_ACCESS_KEY`, `NCP_SECRET_KEY` (필수)
- `NCP_TARGET` : `ncloud`(기본) 또는 `gov`
- `NCP_REGION_CODE` : `KR-1`, `KR-2` 등 필요 시 설정

## 사용 예시
```python
from ncp_client import GOV_BASE_URL, NCPApiClient, NCPCredentials, NCP_BASE_URL

credentials = NCPCredentials(
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
)

client = NCPApiClient(
    credentials=credentials,
    base_url=GOV_BASE_URL,  # 일반 환경이면 NCP_BASE_URL
    default_region="KR-1",
)

response = client.request(
    "GET",
    "/server/v2/getServerInstanceList",
    params={"responseFormatType": "json"},
)
print(response.json())
```

## 월간 보고서 파이프라인 연계
1. `client.request()`로 원하는 API 데이터를 JSON으로 확보
2. 데이터를 가공(통계/차트)
3. 템플릿 엔진(`docxtpl`, `weasyprint` 등)을 사용해 DOCX/PDF 동시 생성
4. cron/GitHub Actions 등으로 월별 자동 실행

필요한 추가 기능이나 보고서 템플릿 자동화를 원하시면 알려주세요.