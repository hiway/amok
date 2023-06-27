from nacl.signing import SigningKey, VerifyKey

from amok import AmokAPI


async def test_init():
    amok = AmokAPI()

    assert amok.signing_key is None
    assert amok.verify_key is None

    await amok.init(name="Example")

    assert isinstance(amok.signing_key, SigningKey)
    assert isinstance(amok.verify_key, VerifyKey)
