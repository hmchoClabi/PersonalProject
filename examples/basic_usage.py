 """
 Minimal example showing how to call any NCP REST API (global or GOV).
 """
 from __future__ import annotations

 import os

 from ncp_client import (
     GOV_BASE_URL,
     NCPApiClient,
     NCPCredentials,
     NCP_BASE_URL,
 )


 def build_client() -> NCPApiClient:
     credentials = NCPCredentials(
         access_key=os.environ["NCP_ACCESS_KEY"],
         secret_key=os.environ["NCP_SECRET_KEY"],
     )

     base_url = GOV_BASE_URL if os.getenv("NCP_TARGET", "ncloud") == "gov" else NCP_BASE_URL

     return NCPApiClient(
         credentials=credentials,
         base_url=base_url,
         default_region=os.getenv("NCP_REGION_CODE"),
     )


 def main() -> None:
     client = build_client()
     response = client.request(
         "GET",
         "/server/v2/getServerInstanceList",
         params={"responseFormatType": "json"},
     )
     print(response.json())


 if __name__ == "__main__":
     main()
