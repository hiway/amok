from dataclasses import dataclass, field


@dataclass
class Peer:
    host: str
    port: int
