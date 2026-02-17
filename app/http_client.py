from __future__ import annotations

from typing import Any, Dict, Optional, Union

import requests

from .tokens import OAuth2Token


class Client:
    def __init__(self) -> None:
        self.oauth2_token: Union[OAuth2Token, Dict[str, Any], None] = None
        self.session = requests.Session()

    def refresh_oauth2(self) -> None:
        self.oauth2_token = OAuth2Token(access_token="fresh-token", expires_at=10**10)

    def request(
        self,
        method: str,
        path: str,
        *,
        api: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        if headers is None:
            headers = {}

        if api:
            if not self.oauth2_token or not isinstance(self.oauth2_token, OAuth2Token) or self.oauth2_token.expired:
                self.refresh_oauth2()

            if isinstance(self.oauth2_token, OAuth2Token):
                headers["Authorization"] = self.oauth2_token.as_header()

        req = requests.Request(method=method, url=f"https://example.com{path}", headers=headers)
        prepared = self.session.prepare_request(req)

        return {
            "method": method,
            "path": path,
            "headers": dict(prepared.headers),
        }