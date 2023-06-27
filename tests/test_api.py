import asyncio

import pytest

from nacl.signing import SigningKey, VerifyKey
from amok import AmokAPI


async def test_init():
    amok = AmokAPI()

    assert amok._signing_key is None
    assert amok._verify_key is None

    await amok.init(name="Example")

    assert isinstance(amok._signing_key, SigningKey)
    assert isinstance(amok._verify_key, VerifyKey)


async def test_init_repeat():
    amok = AmokAPI()

    await amok.init(name="Example")

    signing_key = amok._signing_key
    verify_key = amok._verify_key

    await amok.init(name="Example")

    assert signing_key == amok._signing_key
    assert verify_key == amok._verify_key


async def test_init_different_names():
    amok = AmokAPI()

    await amok.init(name="Example")

    signing_key = amok._signing_key
    verify_key = amok._verify_key

    await amok.init(name="Different")

    assert signing_key != amok._signing_key
    assert verify_key != amok._verify_key


async def test_id():
    amok = AmokAPI()

    await amok.init(name="Example")

    assert len(amok.id.split(":")) == 2
    assert amok.id.split(":")[0] == "Example"


async def test_sign_and_verify():
    amok = AmokAPI()

    await amok.init(name="Example")

    message = b"Hello, World!"
    signed_message = await amok.sign(message)
    signature = signed_message.signature
    assert isinstance(signature, bytes)
    assert len(signature) == 64

    assert await amok.verify(amok.verify_key, signed_message.message, signature)


async def test_payload():
    amok = AmokAPI()

    await amok.start()
    await amok.init(name="Example")
    payload = await amok.payload()
    assert len(payload) == 2
    assert payload["name"] == "Example"
    assert isinstance(payload["verify_key"], str)
    await amok.stop()


async def test_start_stop():
    amok = AmokAPI()

    await amok.start("127.0.0.1", 8070)
    assert amok._dht is not None
    await amok.stop()


async def test_start_with_peers():
    amok = AmokAPI()
    peer = AmokAPI()

    await peer.start("127.0.0.1", 8090)

    await amok.start("127.0.0.1", 8070, [("127.0.0.1", 8090)])
    assert amok._dht is not None

    await amok.stop()
    await peer.stop()


async def test_stop_without_start():
    amok = AmokAPI()

    with pytest.raises(AssertionError):
        await amok.stop()


async def test_post_and_read():
    amok = AmokAPI()
    peer = AmokAPI()

    await peer.start("127.0.0.1", 8090)

    await amok.start("127.0.0.1", 8070, peers=[("127.0.0.1", 8090)])
    await amok.init(name="Example")

    await asyncio.sleep(0.2)

    status = "Hello, World!"
    await amok.post(status)

    async for status_ in amok.read():
        assert status_ == status
        break

    await amok.stop()
    await peer.stop()


async def test_follow(tmp_path):
    amok = AmokAPI(config_path=tmp_path.joinpath("config.json"))
    await amok.start("127.0.0.1", 8071)

    await amok.follow("id1")
    await amok.follow("id2")
    assert await amok.following() == ["id1", "id2"]
    await amok.stop()


async def test_unfollow(tmp_path):
    amok = AmokAPI(config_path=tmp_path.joinpath("config.json"))
    await amok.start("127.0.0.1", 8072)

    await amok.follow("id1")
    await amok.follow("id2")
    await amok.unfollow("id1")
    assert await amok.following() == ["id2"]
    await amok.stop()
