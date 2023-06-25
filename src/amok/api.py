import asyncio
import secrets
from typing import Optional

import keyring
from asgiref.sync import sync_to_async
from itsdangerous import BadSignature, URLSafeTimedSerializer
from kademlia.network import Server as KademliaServer
from passlib.hash import argon2

from amok.logging import get_logger
from amok.models import Peer


logger = get_logger(__name__)


def dht_required(func):
    async def wrapper(self, *args, **kwargs):
        if self.dht:
            return await func(self, *args, **kwargs)
        else:
            raise RuntimeError("API was not started?")

    return wrapper


class AmokAPI:
    def __init__(self):
        self.dht: KademliaServer = None  # type: ignore
        self.username: Optional[str] = None

    async def start(
        self,
        host: str,
        port: int,
        peers: Optional[list[Peer]] = None,
    ) -> None:
        self.dht = KademliaServer()
        await self.dht.listen(port, interface=host)
        logger.info("Listening on %s:%d", host, port)
        if peers:
            await self.dht.bootstrap([(peer.host, peer.port) for peer in peers])
            logger.info("Bootstrapped with %d peers", len(peers))

    @dht_required
    async def stop(self) -> None:
        self.dht.stop()
        logger.info("Stopped")

    @dht_required
    async def get_public_data(self, key: str):
        return await self.dht.get(key)

    @dht_required
    async def set_public_data(self, key: str, value: str):
        return await self.dht.set(key, value)

    async def get_secret_data(self, key: str):
        return await sync_to_async(keyring.get_password)("amok", key)

    async def set_secret_data(self, key: str, value: str):
        await sync_to_async(keyring.set_password)("amok", key, value)

    async def delete_secret_data(self, key: str):
        await sync_to_async(keyring.delete_password)("amok", key)

    async def account_create(self, username: str, password: str) -> None:
        if self.username:
            raise AssertionError(f"Account {self.username!r} already loaded")
        account_exists = await self.get_secret_data("username")
        if account_exists:
            raise AssertionError(f"Account {account_exists!r} already exists")
        else:
            self.username = username
            await self.set_secret_data("username", username)
            await self.set_secret_data("password_hash", argon2.hash(password))

    async def account_login(self, username: str, password: str) -> None:
        if self.username:
            raise AssertionError(f"Account {self.username!r} already loaded")
        else:
            if username != await self.get_secret_data("username"):
                raise KeyError("Invalid username")
            else:
                if not argon2.verify(
                    password, await self.get_secret_data("password_hash")
                ):
                    raise KeyError("Invalid password")
                else:
                    self.username = username
                    logger.info("Logged in as %s", username)

    async def account_token(self) -> str:
        if self.username:
            secret_key = await self.get_secret_data("secret_key")
            if not secret_key:
                secret_key = secrets.token_urlsafe(64)
                await self.set_secret_data("secret_key", secret_key)
            token = URLSafeTimedSerializer(secret_key=secret_key).dumps(self.username)
            if isinstance(token, bytes):
                return token.decode("utf-8")
            else:
                return token
        else:
            raise AssertionError("No account loaded")

    async def account_token_login(self, token: str) -> None:
        if self.username:
            raise AssertionError(f"Account {self.username!r} already loaded")
        else:
            secret_key = await self.get_secret_data("secret_key")
            if not secret_key:
                raise AssertionError("No secret key")
            try:
                username = URLSafeTimedSerializer(secret_key=secret_key).loads(token)
            except BadSignature:
                raise AssertionError("Invalid token")
            else:
                self.username = username

    async def account_logout(self) -> None:
        if self.username:
            self.username = None
            logger.info("Logged out")
        else:
            raise AssertionError("No account loaded")

    async def account_delete(self) -> None:
        if self.username:
            await self.set_secret_data("username", "")
            await self.set_secret_data("password_hash", "")
            self.username = None
            logger.info("Deleted account")
        else:
            raise AssertionError("No account loaded")

    async def account_info(self) -> dict[str, str]:
        if self.username:
            return {
                "username": self.username,
                "token": await self.account_token(),
            }
        else:
            raise AssertionError("No account loaded")
