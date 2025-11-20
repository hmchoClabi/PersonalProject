 from __future__ import annotations

 from dataclasses import dataclass
 from typing import Any, Mapping, MutableMapping, Optional

 import requests

 from .auth import NCPRequestSigner, NCPCredentials

 NCP_BASE_URL = "https://ncloud.apigw.ntruss.com"
 GOV_BASE_URL = "https://gov-ncloud.apigw.ntruss.com"


 class NCPApiError(requests.HTTPError):
     """
     Raised when an API call returns an error response.
     """

     def __init__(self, response: requests.Response) -> None:
         super().__init__(str(response.status_code), response=response)
         self.payload = self._extract_payload(response)

     @staticmethod
     def _extract_payload(response: requests.Response) -> Any:
         try:
             return response.json()
         except ValueError:
             return response.text


 @dataclass
 class NCPClientOptions:
     """
     Optional configuration for the API client.
     """

     base_url: str = NCP_BASE_URL
     timeout: float = 30.0
     default_region: Optional[str] = None


 class NCPApiClient:
     """
     Lightweight wrapper around requests.Session with automatic NCP signing.
     """

     def __init__(
         self,
         credentials: NCPCredentials,
         *,
         base_url: str | None = None,
         signer: NCPRequestSigner | None = None,
         session: requests.Session | None = None,
         timeout: float = 30.0,
         default_headers: Optional[Mapping[str, str]] = None,
         default_region: Optional[str] = None,
     ) -> None:
         self.signer = signer or NCPRequestSigner(credentials)
         self.base_url = (base_url or NCP_BASE_URL).rstrip("/")
         self.session = session or requests.Session()
         self.timeout = timeout
         self.default_headers: MutableMapping[str, str] = dict(default_headers or {})
         self.default_region = default_region

     def close(self) -> None:
         self.session.close()

     def request(
         self,
         method: str,
         path: str,
         *,
         params: Optional[Mapping[str, Any]] = None,
         data: Any = None,
         json: Any = None,
         headers: Optional[Mapping[str, str]] = None,
         region_code: Optional[str] = None,
         timeout: Optional[float] = None,
         raise_for_status: bool = True,
     ) -> requests.Response:
         """
         Executes an authenticated request against the NCP API.
         """
         method = method.upper()
         normalized_path = self._normalize_path(path)
         url = f"{self.base_url}{normalized_path}"

         merged_headers: MutableMapping[str, str] = dict(self.default_headers)
         if headers:
             merged_headers.update(headers)

         request = requests.Request(
             method=method,
             url=url,
             params=params,
             data=data,
             json=json,
             headers=merged_headers,
         )

         prepared = self.session.prepare_request(request)
         timestamp = self.signer.timestamp()
         signed_headers = self.signer.build_headers(
             method=method,
             path=prepared.path_url,
             timestamp=timestamp,
             region_code=region_code or self.default_region,
         )
         prepared.headers.update(signed_headers)

         response = self.session.send(prepared, timeout=timeout or self.timeout)

         if raise_for_status:
             try:
                 response.raise_for_status()
             except requests.HTTPError:
                 raise NCPApiError(response) from None

         return response

     @staticmethod
     def _normalize_path(path: str) -> str:
         if not path:
             raise ValueError("path is required")
         return path if path.startswith("/") else f"/{path}"
