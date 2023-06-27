import click


@click.group()
def main():
    pass


@main.command("init")
def init():
    click.echo("init")


@main.command("id")
def id():
    click.echo("id")


@main.command("post")
def post():
    click.echo("post")


@main.command("read")
def read():
    click.echo("read")


@main.command("follow")
def follow():
    click.echo("follow")


@main.command("unfollow")
def unfollow():
    click.echo("unfollow")


@main.command("config")
@click.option("--edit/-e")
def config():
    click.echo("config")


@main.command("run")
def run():
    click.echo("run")


@main.command("serve")
def serve():
    click.echo("serve")
