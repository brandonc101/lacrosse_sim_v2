from dataclasses import dataclass

@dataclass
class Player:
    name: str
    position: str  # 'Attack', 'Midfield', 'Defense', 'Goalie'
    shooting: int
    passing: int
    defense: int
    stamina: int

    # Match stats
    goals: int = 0
    assists: int = 0
