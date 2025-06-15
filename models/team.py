from dataclasses import dataclass, field
from typing import List
from .player import Player

@dataclass
class Team:
    name: str
    players: List[Player] = field(default_factory=list)

    # Team season stats
    wins: int = 0
    losses: int = 0
    draws: int = 0
    goals_for: int = 0
    goals_against: int = 0
