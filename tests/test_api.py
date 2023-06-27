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

    await amok.init(name="Example")
    payload = await amok.payload()
    assert len(payload) == 2
    assert payload["name"] == "Example"
    assert isinstance(payload["verify_key"], str)


async def test_start_stop():
    amok = AmokAPI()

    await amok.start("127.0.0.1", 8000)
    assert amok._dht is not None
    await amok.stop()


async def test_start_with_peers():
    amok = AmokAPI()
    peer = AmokAPI()

    await peer.start("127.0.0.1", 8001)

    await amok.start("127.0.0.1", 8000, [("127.0.0.1", 8001)])
    assert amok._dht is not None

    await amok.stop()
    await peer.stop()


async def test_stop_without_start():
    amok = AmokAPI()

    with pytest.raises(AssertionError):
        await amok.stop()
