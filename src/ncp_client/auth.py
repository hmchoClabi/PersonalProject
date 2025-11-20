 from __future__ import annotations

 import base64
 import hashlib
 import hmac
 import time
 from dataclasses import dataclass
 from typing import Callable, Dict, Mapping, MutableMapping, Optional


 def _default_timestamp_provider() -> str:
     """
     Returns the current epoch milliseconds as a string.
     """
     return str(int(time.time() * 1000))


 @dataclass(frozen=True)
 class NCPCredentials:
     """
     Simple container for NCP API credentials.
     """

     access_key: str
     secret_key: str

     def validate(self) -> None:
         if not self.access_key:
             raise ValueError("access_key must not be empty")
         if not self.secret_key:
             raise ValueError("secret_key must not be empty")


 class NCPRequestSigner:
     """
     Handles signature generation required by the NCP API Gateway.
     """

     def __init__(
         self,
         credentials: NCPCredentials,
         timestamp_provider: Callable[[], str] | None = None,
     ) -> None:
         credentials.validate()
         self.credentials = credentials
         self._timestamp_provider = timestamp_provider or _default_timestamp_provider

     def timestamp(self) -> str:
         """
         Returns a timestamp string (epoch milliseconds) using the configured provider.
         """
         return self._timestamp_provider()

     def generate_signature(self, method: str, path: str, timestamp: str) -> str:
         if not path.startswith("/"):
             raise ValueError("path must start with '/' when generating the signature")

         canonical = f"{method.upper()} {path}\n{timestamp}\n{self.credentials.access_key}"
         digest = hmac.new(
             self.credentials.secret_key.encode("utf-8"),
             canonical.encode("utf-8"),
             hashlib.sha256,
         ).digest()
         return base64.b64encode(digest).decode("utf-8")

     def build_headers(
         self,
         method: str,
         path: str,
         timestamp: Optional[str] = None,
         *,
         region_code: Optional[str] = None,
         extra_headers: Optional[Mapping[str, str]] = None,
     ) -> Dict[str, str]:
         """
         Creates the minimum set of headers required to call the NCP REST API.
         """
         ts = timestamp or self.timestamp()
         signature = self.generate_signature(method, path, ts)

         headers: MutableMapping[str, str] = {
             "x-ncp-apigw-timestamp": ts,
             "x-ncp-iam-access-key": self.credentials.access_key,
             "x-ncp-apigw-signature-v2": signature,
         }

         if region_code:
             headers["x-ncp-region_code"] = region_code

         if extra_headers:
             headers.update(extra_headers)

         return dict(headers)
