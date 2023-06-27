from typing import Optional

from nacl.signing import SigningKey, VerifyKey


class AmokAPI:
    signing_key: Optional[SigningKey]
    verify_key: Optional[VerifyKey]

    def __init__(self) -> None:
        self.signing_key = None
        self.verify_key = None

    async def init(self, name: str) -> None:
        self.signing_key = SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
