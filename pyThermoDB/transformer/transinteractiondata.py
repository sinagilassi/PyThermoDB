"""Transform interaction rows without matrix expansion."""
from __future__ import annotations
from typing import Any

class TransInteractionData:
    """Normalize API-style interaction payloads while retaining scalar rows."""
    data_type = "interaction-data"

    def __init__(self, api_data_pack: list[dict[str, Any]] | None = None) -> None:
        self.api_data_pack = api_data_pack or []
        self.data_trans_pack: dict[str, Any] = {}

    def trans(self) -> dict[str, Any]:
        # SECTION: preserve table rows and nulls exactly as supplied
        self.data_trans_pack = {"interaction-data": self.api_data_pack}
        return self.data_trans_pack