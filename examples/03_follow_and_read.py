import asyncio
from amok import AmokAPI

amok = AmokAPI()


async def main():
    # Connect to DHT
    await amok.start("127.0.0.1", 8060, [("127.0.0.1", 8090)])

    # Create an account
    await amok.init(name="Example")

    # Amok ID
    print(f"Amok ID: {amok.id}")

    # Follow
    await amok.follow(
        "Hiway:7be788372630cb708ece2512809f46d44e48fca7beb5b2904923072913184bfa"
    )

    await asyncio.sleep(0.2)

    # Read statuses
    print("Statuses:")
    async for status in amok.read():
        print(f"[{status['name']}]: {status['message']}")

    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        # Disconnect from DHT
        await amok.stop()


asyncio.run(main())
