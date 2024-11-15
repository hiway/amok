# Amok

Peer-to-peer Ephemeral Status Updates

> Note: These are planned features, the following is an aspirational readme.
> Once releases start appearing on this project, it should be ready to test.

- Amok uses distributed hash table (DHT) to publish and subscribe to status updates
- Status is text that can be read by anyone subscribed to your Amok ID
- Share your Amok ID with friends or general public
- Follow Amok IDs of people you care about to receive status updates
- No servers, no signups, no ads

---

## Desktop app

```console
$ amok run
```

---

## Web interface

```console
$ amok serve

One-time configuration...

Bind [localhost]: 
Enable TLS [Yes]:
Port [3443]:
Public IPv4/domain: localhost

Starting Amok... ready.

Amok is available at https://localhost:3443/
```

---

## Command-line interface:

### Create an account

```console
$ amok init
Welcome to Amok. Let's begin by creating an account for you.

Your Name/Alias: Hiway

Generating signing keypair for Hiway...
All done, you can now run `amok post` to publish your first status.
```

### Post

```console
$ amok post
Compose your post below and press Ctrl+D when done.

Hello, World!
^D
Publishing... done.

Share your Amok ID with friends. Run `amok id` to get yours.
Follow your friends with `amok follow`.
```

### Your Amok ID

```console
$ amok id

Hiway:9b0c180377a584bf5014a341d6c529ef25e3f7f16d5b19ee7fa7533c7639a27c

```

### Follow a friend using their Amok ID

```console
$ amok follow
Paste Amok ID below: 

Example:c0f98f9eda03c949ca6fa0d2ed462b84933cad5ec5143afcdfe6140cb22cbd5e

Subscribiing... done.

Read followed people's statuses with `amok read`
```

### Check on your friends

```console
$ amok read
[Example]: Twiddling digits.
[Hiway]: Hello, World!
```

---

## Python API

```python
import asyncio
from amok import AmokAPI

amok = AmokAPI()

async def main():
    # Connect to DHT
    await amok.start()

    # Create an account
    await amok.init(name="Hiway")

    # Post a status
    status = "Hello, World!"
    await amok.post(status)

    # Amok ID
    print(f"Amok ID: {amok.id}")

    # Follow
    await amok.follow("Example:c0f98f9eda03c949ca6fa0d2ed462b84933cad5ec5143afcdfe6140cb22cbd5e")

    # Read statuses
    print("Statuses:")
    async for status in amok.read():
        print(f"[{status.name}]: {status.message}")

    # Disconnect from DHT
    await amok.stop()


asyncio.run(main())
```