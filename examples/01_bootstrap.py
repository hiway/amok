import asyncio
from amok import AmokAPI

amok = AmokAPI()


async def main():
    # Connect to DHT
    await amok.start("127.0.0.1", 8090)

    # Create an account
    await amok.init(name="Bootstrap")

    # Amok ID
    print(f"Amok ID: {amok.id}")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        # Disconnect from DHT
        await amok.stop()


asyncio.run(main())
