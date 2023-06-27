import json
from base64 import b64encode, b64decode
from hashlib import sha256
from secrets import token_bytes
from typing import Optional

import keyring
from kademlia.network import Server as KademliaServer
from nacl.signing import SigningKey, VerifyKey, SignedMessage
from nacl.encoding import Base64Encoder


class AmokAPI:
    def __init__(self) -> None:
        self.name: Optional[str] = None
        self._signing_key: Optional[SigningKey] = None
        self._verify_key: Optional[VerifyKey] = None
        self._dht: Optional[KademliaServer] = None

    @property
    def id(self) -> str:
        assert self._verify_key
        return sha256(self._verify_key.encode(Base64Encoder)).hexdigest()

    @property
    def verify_key(self) -> str:
        assert self._verify_key
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
        assert self._signing_key
        return self._signing_key.sign(message)

    async def verify(self, verify_key: str, message: bytes, signature: bytes) -> bool:
        try:
            _verify_key = VerifyKey(verify_key.encode("utf-8"), Base64Encoder)
            _verify_key.verify(message, signature)
            return True
        except Exception:
            return False

    async def start(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        peers: Optional[list[tuple]] = None,
    ):
        self._dht = KademliaServer()
        await self._dht.listen(port, interface=host)
        if peers:
            await self._dht.bootstrap(peers)

    async def stop(self):
        assert self._dht
        self._dht.stop()

    async def payload(self) -> dict:
        assert self._dht
        published_payload = await self._dht.get(self.id)
        if published_payload:
            _payload = json.loads(published_payload)
            if not _payload["name"] == self.name:
                _payload = {}
            if not _payload["verify_key"] == self.verify_key:
                _payload = {}
        else:
            _payload = {}

        if not _payload:
            _payload = {
                "name": self.name,
                "verify_key": self.verify_key,
            }

        return _payload

    async def post(self, status: str) -> None:
        assert self._dht
        payload = await self.payload()
        # todo: list of statuses
        payload["status"] = status
        await self._dht.set(self.id, json.dumps(payload))

    async def read(self, id: Optional[str] = None) -> Optional[str]:
        assert self._dht
        if not id:
            id = self.id
        payload_ = await self._dht.get(id)
        if not payload_:
            return None
        payload = json.loads(payload_)
        return payload.get("status", None)
