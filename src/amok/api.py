from base64 import b64encode, b64decode
from secrets import token_bytes
from typing import Optional

import keyring
from nacl.signing import SigningKey, VerifyKey, SignedMessage
from nacl.encoding import Base64Encoder


class AmokAPI:
    def __init__(self) -> None:
        self.name: Optional[str] = None
        self._signing_key: Optional[SigningKey] = None
        self._verify_key: Optional[VerifyKey] = None

    @property
    def verify_key(self) -> str:
        assert self._verify_key is not None
        return self._verify_key.encode(Base64Encoder).decode("utf-8")

    async def init(self, name: str) -> None:
        self.name = name
        seed = keyring.get_password("amok", name)
        if seed is None:
            seed = token_bytes(32)
            keyring.set_password("amok", name, b64encode(seed).decode("utf-8"))
        else:
            seed = b64decode(seed)
        self._signing_key = SigningKey(seed)
        self._verify_key = self._signing_key.verify_key

    async def sign(self, message: bytes) -> SignedMessage:
        assert self._signing_key is not None
        return self._signing_key.sign(message)

    async def verify(self, verify_key: str, message: bytes, signature: bytes) -> bool:
        try:
            _verify_key = VerifyKey(verify_key.encode("utf-8"), Base64Encoder)
            _verify_key.verify(message, signature)
            return True
        except Exception:
            return False

    async def payload(self):
        return {
            "name": self.name,
            "verify_key": self.verify_key,
        }
