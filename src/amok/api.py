import json
from base64 import b64encode, b64decode
from hashlib import sha256
from pathlib import Path
from secrets import token_bytes
from typing import AsyncIterator, Optional

import keyring
from click import get_app_dir
from kademlia.network import Server as KademliaServer
from nacl.signing import SigningKey, VerifyKey, SignedMessage
from nacl.encoding import Base64Encoder


class AmokAPI:
    def __init__(self, config_path: Optional[Path] = None) -> None:
        self.name: Optional[str] = None
        self._signing_key: Optional[SigningKey] = None
        self._verify_key: Optional[VerifyKey] = None
        self._dht: Optional[KademliaServer] = None
        self._config_path = config_path

    @property
    def id(self) -> str:
        assert self._verify_key
        assert self.name
        hash = sha256(self._verify_key.encode(Base64Encoder)).hexdigest()
        return f"{self.name}:{hash}"

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
        self._config_path = Path(get_app_dir("amok")).joinpath(f"{self.name}.json")
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

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
        signed_message = await self.sign(status.encode("utf-8"))
        payload["message"] = signed_message.message.decode("utf-8")
        payload["signature"] = b64encode(signed_message.signature).decode("utf-8")

        await self._dht.set(self.id, json.dumps(payload))

    async def read(self) -> AsyncIterator[dict]:
        assert self._dht
        following = await self.following()
        following.append(self.id)
        for id in following:
            payload_ = await self._dht.get(id)
            if not payload_:
                continue
            payload = json.loads(payload_)
            if not payload.get("message"):
                continue
            # Verify
            if not await self.verify(
                payload["verify_key"],
                payload["message"].encode("utf-8"),
                b64decode(payload["signature"]),
            ):
                continue
            yield payload

    async def follow(self, id: str):
        assert self._dht
        assert self._config_path
        if self._config_path.exists():
            with open(self._config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
        if not config.get("follows"):
            config["follows"] = []
        if id not in config["follows"]:
            config["follows"].append(id)
        with open(self._config_path, "w") as f:
            json.dump(config, f)

    async def unfollow(self, id: str):
        assert self._dht
        assert self._config_path
        if self._config_path.exists():
            with open(self._config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
        if not config.get("follows"):
            config["follows"] = []
        if id in config["follows"]:
            config["follows"].remove(id)
        with open(self._config_path, "w") as f:
            json.dump(config, f)

    async def following(self):
        assert self._dht
        assert self._config_path
        if self._config_path.exists():
            with open(self._config_path, "r") as f:
                config = json.load(f)
        else:
            config = {}
        if not config.get("follows"):
            config["follows"] = []
        return config["follows"]
