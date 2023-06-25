import asyncio

import click

from amok.api import AmokAPI
from amok.models import Peer


@click.group()
def main():
    pass


@main.command("bootstrap")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=3030, show_default=True)
def main_bootstrap(host: str, port: int):
    api = AmokAPI()

    async def _bootstrap_node():
        await api.start(host, port)
        while True:
            await asyncio.sleep(1)

    asyncio.run(_bootstrap_node())


@main.command("run")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=3000, show_default=True)
@click.option("--peer", default=["127.0.0.1:3030"], multiple=True, show_default=True)
def main_run(host: str, port: int, peer: str):
    api = AmokAPI()

    async def _run_node():
        peers = []
        if peer:
            for peer_str in peer:
                _host, _port = peer_str.split(":")
                peers.append(Peer(host=_host, port=int(_port)))

        peers_str = await api.get_secret_data("peers")
        if peers_str:
            for peer_str in peers_str.split(","):
                _host, _port = peer_str.split(":")
                peers.append(Peer(host=_host, port=int(_port)))

        await api.start(host, port, peers)
        while True:
            await asyncio.sleep(1)

    asyncio.run(_run_node())


@main.group("account")
def main_account():
    pass


@main_account.command("create")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
def main_account_create(username: str, password: str):
    api = AmokAPI()

    async def _account_create():
        username_exists = await api.get_secret_data("username")
        if username_exists:
            click.echo(f"Account {username_exists!r} already exists")
            raise click.Abort()
        await api.account_create(username, password)

    asyncio.run(_account_create())


@main_account.command("login")
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def main_account_login(username: str, password: str):
    api = AmokAPI()

    async def _account_login():
        await api.account_login(username, password)
        token = await api.account_token()
        await api.set_secret_data("token", token)

    asyncio.run(_account_login())


@main_account.command("logout")
def main_account_logout():
    api = AmokAPI()

    async def _account_logout():
        await api.account_logout()
        await api.delete_secret_data("token")

    asyncio.run(_account_logout())


@main_account.command("info")
def main_account_info():
    api = AmokAPI()

    async def _account_info():
        token = await api.get_secret_data("token")
        if not token:
            click.echo("Not logged in")
            raise click.Abort()
        await api.account_token_login(token)
        print(await api.account_info())

    asyncio.run(_account_info())


@main_account.command("delete")
def main_account_delete():
    api = AmokAPI()

    async def _account_delete():
        token = await api.get_secret_data("token")
        if not token:
            click.echo("Not logged in")
            raise click.Abort()
        await api.account_token_login(token)
        await api.account_delete()

    asyncio.run(_account_delete())


@main.group("peer")
def main_peer():
    pass


@main_peer.command("list")
def main_peer_list():
    api = AmokAPI()

    async def _peer_list():
        peers_str = await api.get_secret_data("peers")
        if not peers_str:
            click.echo("No peers set")
            return
        for peer in peers_str.split(","):
            click.echo(peer)

    asyncio.run(_peer_list())


@main_peer.command("add")
@click.option("--peer", prompt=True)
def main_peer_add(peer: str):
    if ":" not in peer:
        click.echo("Peer must be in format <host>:<port>")
        raise click.Abort()

    api = AmokAPI()

    async def _peer_add():
        peers_str = await api.get_secret_data("peers")
        if peers_str:
            peers = peers_str.split(",")
        else:
            peers = []
        peers.append(peer)
        await api.set_secret_data("peers", ",".join(peers))
        click.echo(f"Added peer {peer!r}")

    asyncio.run(_peer_add())


@main_peer.command("remove")
@click.option("--peer", prompt=True)
def main_peer_remove(peer: str):
    api = AmokAPI()

    async def _peer_remove():
        peers_str = await api.get_secret_data("peers")
        if not peers_str:
            click.echo("No peers set")
            return
        peers = peers_str.split(",")
        if peer not in peers:
            click.echo(f"Peer {peer!r} not in peers")
            return
        peers.remove(peer)
        await api.set_secret_data("peers", ",".join(peers))
        click.echo(f"Removed peer {peer!r}")

    asyncio.run(_peer_remove())
