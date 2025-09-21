import random
from models.player import Player
from models.team import Team

def create_balanced_team(name: str) -> Team:
    team = Team(name)
    players = []

    position_counts = {
        "Attacker": 7,
        "Midfielder": 8,
        "Defense": 7,
        "Goalie": 3
    }

    skill_ranges = {
        "Attacker": {"shooting": (70, 95), "passing": (60, 85), "defense": (40, 65), "stamina": (70, 90)},
        "Midfielder": {"shooting": (60, 85), "passing": (70, 95), "defense": (50, 75), "stamina": (75, 95)},
        "Defense": {"shooting": (40, 65), "passing": (50, 70), "defense": (80, 95), "stamina": (65, 85)},
        "Goalie": {"shooting": (10, 30), "passing": (40, 60), "defense": (85, 95), "stamina": (60, 80)}
    }

    for position, count in position_counts.items():
        for i in range(count):
            name_suffix = f"{position[:3]}_{i+1}"
            player_name = f"{name} Player {name_suffix}"

            sr = skill_ranges[position]
            shooting = random.randint(*sr["shooting"])
            passing = random.randint(*sr["passing"])
            defense = random.randint(*sr["defense"])
            stamina = random.randint(*sr["stamina"])

            player = Player(player_name, position, shooting, passing, defense, stamina)
            players.append(player)

    team.players = players
    return team
